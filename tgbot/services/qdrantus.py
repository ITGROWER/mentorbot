from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from uuid import uuid4

# Инициализация клиента Qdrant
qdrant = QdrantClient(host="qdrant", port=6333)
COLLECTION_NAME = "user_chat_memory"
VECTOR_SIZE = 1536  # под размер embedding от OpenAI


# Один раз при старте — создать коллекцию
def init_qdrant():
    qdrant.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
    )


# Добавление сообщения в память
def store_message(user_id: int, role: str, content: str, embedding: list[float]):
    qdrant.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            PointStruct(
                id=str(uuid4()),
                vector=embedding,
                payload={
                    "user_id": user_id,
                    "role": role,
                    "content": content,
                },
            )
        ],
    )


# Поиск наиболее похожих сообщений
def retrieve_history(user_id: int, query_embedding: list[float], top_k=5):
    hits = qdrant.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_embedding,
        limit=top_k,
        query_filter={"must": [{"key": "user_id", "match": {"value": user_id}}]},
    )
    return [hit.payload["content"] for hit in hits]
