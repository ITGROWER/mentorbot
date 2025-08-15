import os
import httpx
from httpx_socks import AsyncProxyTransport, SyncProxyTransport
import openai
from openai.types.responses import Response, ResponseUsage
from langchain_openai import OpenAIEmbeddings  # Или другая модель для эмбеддингов
from langchain_community.vectorstores import Qdrant
from qdrant_client import QdrantClient
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

from tgbot.misc.logger import logger

# MODEL = "gpt-4o-mini"
# MODEL = "gpt-4-turbo"
MODEL = "gpt-4o"

proxy_user = os.getenv("XRAY_USER", "bot")
proxy_pass = os.getenv("XRAY_PASS", "supersecret")
proxy = f"socks5://{proxy_user}:{proxy_pass}@xray:1080"

transport = AsyncProxyTransport.from_url(proxy)
client_http = httpx.AsyncClient(transport=transport)
sync_transport = SyncProxyTransport.from_url(proxy)
client_http_sync = httpx.Client(transport=sync_transport)


client = openai.AsyncOpenAI(
    api_key=os.environ["OPENAI_API_KEY"], http_client=client_http
)


async def init_mentor(user_msg: str):
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": user_msg,
                }
            ],
        },
    ]
    resp: Response = await client.responses.create(
        prompt={
            "id": "pmpt_687fdc2e9d988197b78d6d9ec73ed7b9007fa912406f701e",
            "version": "9",
        },
        model=MODEL,
        input=messages,
        temperature=1,
        max_output_tokens=512,  # limit output size
    )
    # print(resp)
    content = resp.output_text
    usage: ResponseUsage = resp.usage
    cost = (usage.input_tokens * 2.50 + usage.output_tokens * 10.00) / 1_000_000
    print(content)
    logger.debug(f"\nUsed {usage.total_tokens} tokens, cost ≈ ${cost}")
    return content


async def reply_from_mentor(
    user_msg: str, conversation_history: list, mentor_json: dict
):
    # TODO починить форматирование ответов
    messages = [
        {"role": "system", "content": mentor_json},
    ]
    messages.extend(conversation_history)
    messages.append(
        {
            "role": "user",
            "content": user_msg,
        },
    )
    resp: Response = await client.responses.create(
        model=MODEL,
        prompt={
            "id": "pmpt_6880ca9b0ed4819680b74f8820d725e10081c6a730e57326",
            "version": "2",
        },
        input=messages,
        temperature=1,
        max_output_tokens=512,  # limit output size
    )
    content = resp.output_text
    usage: ResponseUsage = resp.usage
    cost = (usage.input_tokens * 0.15 + usage.output_tokens * 0.60) / 1_000_000
    # print(content)
    logger.debug(f"\nUsed {usage.total_tokens} tokens, cost ≈ ${cost:.6f}")
    return content


async def create_embeddings(text: str):
    embeddings = OpenAIEmbeddings(
        openai_api_key=os.environ["OPENAI_API_KEY"],
        http_client=client_http_sync,  # Синхронный клиент для эмбеддингов
    )
    return embeddings.embed_query(text)


async def reply_from_mentor_with_rag(
    user_msg: str,
    conversation_history: list,  # История из FSM или БД
    mentor_json: dict,
    # Дополнительно: ID пользователя или диалога для поиска персональных данных
    user_id: int,
):

    system_prompt_content = mentor_json
    #     --- Интеграция LangChain + Qdrant ---
    # 2. Настройка LLM (используя уже настроенный client)
    llm = ChatOpenAI(
        model_name=MODEL,
        openai_api_key=os.environ["OPENAI_API_KEY"],
        http_client=client_http,  # Передача настроенного клиента
        temperature=1,
        max_tokens=512,
    )

    # 3. Настройка эмбеддингов (для поиска)
    embeddings = OpenAIEmbeddings(
        openai_api_key=os.environ["OPENAI_API_KEY"],
        http_client=client_http_sync,  # Синхронный клиент для эмбеддингов
    )

    # 4. Подключение к Qdrant
    qdrant_client = QdrantClient(
        host="qdrant",  # Имя сервиса из docker-compose
        port=6333,
        # api_key=... # если нужна аутентификация
    )

    # 5. Создание или получение коллекции в Qdrant для этого пользователя/ментора
    collection_name = f"user_{user_id}_chat_history"
    vectorstore = Qdrant(
        client=qdrant_client, collection_name=collection_name, embeddings=embeddings
    )

    # 6. Создание Retriever
    retriever = vectorstore.as_retriever(
        search_kwargs={"k": 3}
    )  # Найти 3 самых релевантных документа

    # 7. Создание PromptTemplate (опционально, для большего контроля)
    prompt_template = PromptTemplate.from_template(
        "System: {system_info}\n"
        "Context (from retrieved docs): {context}\n"
        "Chat History: {chat_history}\n"
        "Human: {question}\n"
        "AI:"
    )
    memory = ConversationBufferMemory(
        memory_key="chat_history",  # Ключ для истории в промпте
        input_key="question",  # Ключ для вопроса пользователя
        output_key="answer",  # Ключ для ответа (если используется в цепочке)
        return_messages=True,  # Возвращать как список сообщений
    )

    # Заполнение памяти из conversation_history
    for msg in conversation_history:
        if msg["role"] == "user":
            memory.chat_memory.add_user_message(msg["content"])
        elif msg["role"] == "assistant":
            memory.chat_memory.add_ai_message(msg["content"])

    # 9. Создание цепочки RAG
    rag_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        # memory=memory, # Можно использовать память цепочки, но мы управляем ею через FSM
        combine_docs_chain_kwargs={
            "prompt": prompt_template
        },  # Использование кастомного промпта
        return_source_documents=True,  # Чтобы видеть, какие документы были использованы
    )
    # 10. Вызов цепочки
    inputs = {
        "system_info": system_prompt_content,
        "question": user_msg,
        "chat_history": conversation_history,  # Передаем историю напрямую
    }
    result = await rag_chain.ainvoke(inputs)  # Асинхронный вызов
    ai_reply = result["answer"]
    source_docs = result.get("source_documents", [])
    logger.debug(ai_reply)
    logger.debug(source_docs)

    return ai_reply
