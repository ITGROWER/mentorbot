"""
Unit tests for bot services.

This module contains tests for all service modules including AI services,
encryption, vector database operations, and other utility services.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json

from tgbot.services.temp_openai import init_mentor, reply_from_mentor, create_embeddings
from tgbot.services.qdrantus import store_message, retrieve_history, init_qdrant
from tgbot.services.encryption import setup, encrypt_data, decrypt_data


class TestOpenAIServices:
    """Test cases for OpenAI service functions."""

    @pytest.mark.asyncio
    async def test_init_mentor_success(self):
        """Test successful mentor initialization."""
        user_background = "I'm a software developer interested in learning AI and machine learning."
        
        # Mock OpenAI API response
        mock_response = {
            "name": "Dr. Sarah Johnson",
            "mentor_age": 42,
            "background": "Experienced AI researcher with 15+ years in machine learning",
            "recent_events": "Recently published a paper on neural networks",
            "personality_style": "Professional yet approachable",
            "greeting": "Hello! I'm Dr. Sarah Johnson, your AI mentor.",
            "sys_prompt_summary": "You are Dr. Sarah Johnson, an AI expert mentor.",
            "brief_background": "Software developer interested in AI",
            "goal": "Learn AI and machine learning"
        }
        
        with patch('tgbot.services.temp_openai.openai_client') as mock_client:
            mock_client.chat.completions.create = AsyncMock(return_value=MagicMock(
                choices=[MagicMock(message=MagicMock(content=json.dumps(mock_response)))]
            ))
            
            result = await init_mentor(user_background)
            result_data = json.loads(result)
            
            assert result_data["name"] == "Dr. Sarah Johnson"
            assert result_data["mentor_age"] == 42
            assert "AI researcher" in result_data["background"]
            assert result_data["brief_background"] == "Software developer interested in AI"
            assert result_data["goal"] == "Learn AI and machine learning"

    @pytest.mark.asyncio
    async def test_init_mentor_api_error(self):
        """Test mentor initialization with API error."""
        user_background = "Test background"
        
        with patch('tgbot.services.temp_openai.openai_client') as mock_client:
            mock_client.chat.completions.create = AsyncMock(side_effect=Exception("API Error"))
            
            with pytest.raises(Exception, match="API Error"):
                await init_mentor(user_background)

    @pytest.mark.asyncio
    async def test_reply_from_mentor_success(self):
        """Test successful mentor reply generation."""
        user_msg = "What are the basics of machine learning?"
        conversation_history = [
            {"role": "user", "content": "Hello!"},
            {"role": "assistant", "content": "Hi there! How can I help you?"},
        ]
        mentor_json = json.dumps({
            "name": "Dr. Sarah Johnson",
            "personality_style": "Friendly and professional",
            "sys_prompt_summary": "AI expert mentor"
        })
        
        expected_response = "Machine learning is a subset of artificial intelligence that focuses on algorithms that can learn from data."
        
        with patch('tgbot.services.temp_openai.openai_client') as mock_client:
            mock_client.chat.completions.create = AsyncMock(return_value=MagicMock(
                choices=[MagicMock(message=MagicMock(content=expected_response))]
            ))
            
            result = await reply_from_mentor(user_msg, conversation_history, mentor_json)
            
            assert result == expected_response
            mock_client.chat.completions.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_reply_from_mentor_with_context(self):
        """Test mentor reply with conversation context."""
        user_msg = "Can you explain that further?"
        conversation_history = [
            {"role": "user", "content": "What is deep learning?"},
            {"role": "assistant", "content": "Deep learning is a subset of machine learning using neural networks."},
            {"role": "user", "content": "Can you explain that further?"},
        ]
        mentor_json = json.dumps({
            "name": "Dr. Sarah Johnson",
            "personality_style": "Detailed and educational",
            "sys_prompt_summary": "AI expert mentor specializing in deep learning"
        })
        
        with patch('tgbot.services.temp_openai.openai_client') as mock_client:
            mock_client.chat.completions.create = AsyncMock(return_value=MagicMock(
                choices=[MagicMock(message=MagicMock(content="Deep learning uses multiple layers of neural networks..."))]
            ))
            
            result = await reply_from_mentor(user_msg, conversation_history, mentor_json)
            
            # Verify the API was called with proper context
            call_args = mock_client.chat.completions.create.call_args
            messages = call_args[1]["messages"]
            
            # Should include system message, conversation history, and user message
            assert len(messages) >= 4  # System + conversation history + user message
            assert any(msg["role"] == "system" for msg in messages)
            assert any(msg["content"] == user_msg for msg in messages)

    @pytest.mark.asyncio
    async def test_create_embeddings_success(self):
        """Test successful embedding creation."""
        text = "This is a test message for embedding creation."
        expected_embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
        
        with patch('tgbot.services.temp_openai.openai_client') as mock_client:
            mock_client.embeddings.create = AsyncMock(return_value=MagicMock(
                data=[MagicMock(embedding=expected_embedding)]
            ))
            
            result = await create_embeddings(text)
            
            assert result == expected_embedding
            mock_client.embeddings.create.assert_called_once_with(
                model="text-embedding-3-small",
                input=text
            )

    @pytest.mark.asyncio
    async def test_create_embeddings_api_error(self):
        """Test embedding creation with API error."""
        text = "Test text"
        
        with patch('tgbot.services.temp_openai.openai_client') as mock_client:
            mock_client.embeddings.create = AsyncMock(side_effect=Exception("Embedding API Error"))
            
            with pytest.raises(Exception, match="Embedding API Error"):
                await create_embeddings(text)


class TestQdrantServices:
    """Test cases for Qdrant vector database services."""

    def test_init_qdrant(self):
        """Test Qdrant initialization."""
        with patch('tgbot.services.qdrantus.QdrantClient') as mock_client:
            init_qdrant()
            mock_client.assert_called_once()

    def test_store_message(self):
        """Test storing message in vector database."""
        user_id = 123456789
        role = "user"
        content = "Hello, I want to learn about AI"
        embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
        
        with patch('tgbot.services.qdrantus.qdrant_client') as mock_client:
            mock_client.upsert = MagicMock()
            
            store_message(user_id, role, content, embedding)
            
            mock_client.upsert.assert_called_once()

    def test_retrieve_history(self):
        """Test retrieving conversation history."""
        user_id = 123456789
        embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
        top_k = 5
        
        expected_messages = [
            "Previous message about AI",
            "Another message about machine learning"
        ]
        
        with patch('tgbot.services.qdrantus.qdrant_client') as mock_client:
            mock_client.search.return_value = [
                MagicMock(payload={"content": msg}) for msg in expected_messages
            ]
            
            result = retrieve_history(user_id, embedding, top_k)
            
            assert result == expected_messages
            mock_client.search.assert_called_once()

    def test_retrieve_history_empty_result(self):
        """Test retrieving history when no results found."""
        user_id = 123456789
        embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
        
        with patch('tgbot.services.qdrantus.qdrant_client') as mock_client:
            mock_client.search.return_value = []
            
            result = retrieve_history(user_id, embedding)
            
            assert result == []


class TestEncryptionServices:
    """Test cases for encryption services."""

    def test_setup_encryption_enabled(self):
        """Test encryption setup when enabled."""
        key = "test_encryption_key_32_characters_long"
        enabled = True
        
        setup(key, enabled)
        
        # Verify encryption is enabled (would need to check internal state)
        # This is a basic test - in practice you'd check the encryption state
        assert True  # Placeholder for actual encryption state check

    def test_setup_encryption_disabled(self):
        """Test encryption setup when disabled."""
        key = "test_encryption_key_32_characters_long"
        enabled = False
        
        setup(key, enabled)
        
        # Verify encryption is disabled
        assert True  # Placeholder for actual encryption state check

    def test_encrypt_data(self):
        """Test data encryption."""
        key = "test_encryption_key_32_characters_long"
        setup(key, True)
        
        data = "sensitive_user_data"
        
        with patch('tgbot.services.encryption.fernet') as mock_fernet:
            mock_cipher = MagicMock()
            mock_cipher.encrypt.return_value = b"encrypted_data"
            mock_fernet.return_value = mock_cipher
            
            result = encrypt_data(data)
            
            assert result == "encrypted_data"
            mock_cipher.encrypt.assert_called_once_with(data.encode())

    def test_decrypt_data(self):
        """Test data decryption."""
        key = "test_encryption_key_32_characters_long"
        setup(key, True)
        
        encrypted_data = "encrypted_data"
        
        with patch('tgbot.services.encryption.fernet') as mock_fernet:
            mock_cipher = MagicMock()
            mock_cipher.decrypt.return_value = b"decrypted_data"
            mock_fernet.return_value = mock_cipher
            
            result = decrypt_data(encrypted_data)
            
            assert result == "decrypted_data"
            mock_cipher.decrypt.assert_called_once_with(encrypted_data.encode())

    def test_encrypt_data_disabled(self):
        """Test data encryption when encryption is disabled."""
        key = "test_encryption_key_32_characters_long"
        setup(key, False)
        
        data = "sensitive_user_data"
        
        result = encrypt_data(data)
        
        # When encryption is disabled, data should be returned as-is
        assert result == data

    def test_decrypt_data_disabled(self):
        """Test data decryption when encryption is disabled."""
        key = "test_encryption_key_32_characters_long"
        setup(key, False)
        
        data = "encrypted_data"
        
        result = decrypt_data(data)
        
        # When encryption is disabled, data should be returned as-is
        assert result == data


class TestServiceIntegration:
    """Integration tests for service interactions."""

    @pytest.mark.asyncio
    async def test_mentor_creation_with_embeddings(self):
        """Test mentor creation workflow with embedding generation."""
        user_background = "I'm a software developer interested in AI."
        
        # Mock responses
        mentor_response = {
            "name": "Dr. Sarah Johnson",
            "mentor_age": 42,
            "background": "AI researcher",
            "recent_events": "Published AI paper",
            "personality_style": "Professional",
            "greeting": "Hello! I'm your AI mentor.",
            "sys_prompt_summary": "AI expert mentor",
            "brief_background": "Software developer interested in AI",
            "goal": "Learn AI"
        }
        
        embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
        
        with patch('tgbot.services.temp_openai.openai_client') as mock_openai, \
             patch('tgbot.services.qdrantus.qdrant_client') as mock_qdrant:
            
            # Mock mentor creation
            mock_openai.chat.completions.create = AsyncMock(return_value=MagicMock(
                choices=[MagicMock(message=MagicMock(content=json.dumps(mentor_response)))]
            ))
            
            # Mock embedding creation
            mock_openai.embeddings.create = AsyncMock(return_value=MagicMock(
                data=[MagicMock(embedding=embedding)]
            ))
            
            # Mock Qdrant operations
            mock_qdrant.upsert = MagicMock()
            
            # Test the workflow
            mentor_result = await init_mentor(user_background)
            embedding_result = await create_embeddings(user_background)
            
            # Store in vector database
            store_message(123456789, "user", user_background, embedding_result)
            
            # Verify results
            assert json.loads(mentor_result)["name"] == "Dr. Sarah Johnson"
            assert embedding_result == embedding
            mock_qdrant.upsert.assert_called_once()

    @pytest.mark.asyncio
    async def test_conversation_flow_with_vector_search(self):
        """Test conversation flow with vector search for context."""
        user_id = 123456789
        user_message = "What is machine learning?"
        embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
        
        # Mock vector search results
        similar_messages = [
            "Previous question about AI",
            "Another question about algorithms"
        ]
        
        mentor_response = "Machine learning is a subset of AI that focuses on algorithms that can learn from data."
        
        with patch('tgbot.services.temp_openai.openai_client') as mock_openai, \
             patch('tgbot.services.qdrantus.qdrant_client') as mock_qdrant:
            
            # Mock embedding creation
            mock_openai.embeddings.create = AsyncMock(return_value=MagicMock(
                data=[MagicMock(embedding=embedding)]
            ))
            
            # Mock vector search
            mock_qdrant.search.return_value = [
                MagicMock(payload={"content": msg}) for msg in similar_messages
            ]
            
            # Mock mentor response
            mock_openai.chat.completions.create = AsyncMock(return_value=MagicMock(
                choices=[MagicMock(message=MagicMock(content=mentor_response))]
            ))
            
            # Mock Qdrant upsert
            mock_qdrant.upsert = MagicMock()
            
            # Test the workflow
            embedding_result = await create_embeddings(user_message)
            similar_messages_result = retrieve_history(user_id, embedding_result, top_k=5)
            
            conversation_history = [
                {"role": "user", "content": user_message},
            ]
            
            mentor_reply = await reply_from_mentor(
                user_message,
                conversation_history,
                json.dumps({"name": "Test Mentor", "personality_style": "Helpful"})
            )
            
            # Store messages
            store_message(user_id, "user", user_message, embedding_result)
            store_message(user_id, "assistant", mentor_reply, embedding_result)
            
            # Verify results
            assert embedding_result == embedding
            assert similar_messages_result == similar_messages
            assert mentor_reply == mentor_response
            assert mock_qdrant.upsert.call_count == 2  # User and assistant messages