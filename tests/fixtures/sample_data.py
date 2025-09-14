"""
Sample data fixtures for testing.

This module provides sample data that can be used across different test modules
to ensure consistency and reduce duplication.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any

from tgbot.db.models.user import DBUser
from tgbot.db.models.mentor import DBMentor
from tgbot.db.models.conversation import DBConversationMessage


def get_sample_user_data() -> Dict[str, Any]:
    """
    Get sample user data for testing.
    
    Returns:
        Dict containing sample user data
    """
    return {
        "name": "John Doe",
        "username": "johndoe",
        "telegram_id": "123456789",
        "brief_background": "Software developer with 5 years of experience in web development",
        "goal": "Learn AI and machine learning to transition into AI engineering",
        "is_sub": False,
        "is_reg": False,
        "is_ban": False,
        "sub_until": None,
    }


def get_sample_user_data_with_subscription() -> Dict[str, Any]:
    """
    Get sample user data with active subscription.
    
    Returns:
        Dict containing sample user data with subscription
    """
    return {
        "name": "Jane Smith",
        "username": "janesmith",
        "telegram_id": "987654321",
        "brief_background": "Data scientist interested in deep learning",
        "goal": "Master advanced machine learning techniques",
        "is_sub": True,
        "is_reg": True,
        "is_ban": False,
        "sub_until": datetime.utcnow() + timedelta(days=30),
    }


def get_sample_user_data_banned() -> Dict[str, Any]:
    """
    Get sample banned user data.
    
    Returns:
        Dict containing sample banned user data
    """
    return {
        "name": "Banned User",
        "username": "banneduser",
        "telegram_id": "111111111",
        "brief_background": "User who violated terms",
        "goal": "Learn AI",
        "is_sub": False,
        "is_reg": True,
        "is_ban": True,
        "sub_until": None,
    }


def get_sample_mentor_data() -> Dict[str, Any]:
    """
    Get sample mentor data for testing.
    
    Returns:
        Dict containing sample mentor data
    """
    return {
        "name": "Dr. Sarah Johnson",
        "mentor_age": 42,
        "background": "Experienced AI researcher with 15+ years in machine learning and neural networks. PhD in Computer Science from MIT, published 50+ papers in top-tier conferences.",
        "recent_events": "Recently published a breakthrough paper on transformer architectures and completed a course on advanced deep learning techniques. Currently working on explainable AI research.",
        "personality_style": "Professional yet approachable, encouraging, patient, and detail-oriented. Loves to break down complex concepts into understandable parts.",
        "greeting": "Hello! I'm Dr. Sarah Johnson, and I'm thrilled to be your AI mentor. I understand you're interested in learning about artificial intelligence and machine learning. What specific area would you like to explore first?",
        "sys_prompt_summary": "You are Dr. Sarah Johnson, an experienced AI researcher and mentor with deep expertise in machine learning, neural networks, and AI applications. You're friendly, encouraging, and have a talent for making complex topics accessible.",
    }


def get_sample_mentor_data_business() -> Dict[str, Any]:
    """
    Get sample business mentor data for testing.
    
    Returns:
        Dict containing sample business mentor data
    """
    return {
        "name": "Michael Chen",
        "mentor_age": 38,
        "background": "Successful tech entrepreneur and business strategist with 12+ years of experience. Founded two AI startups, one of which was acquired by Google. MBA from Stanford.",
        "recent_events": "Recently launched a new AI consulting firm and completed a course on AI ethics in business. Currently advising several AI startups on growth strategies.",
        "personality_style": "Strategic, motivational, and results-oriented. Focuses on practical applications and business impact of AI technologies.",
        "greeting": "Hi there! I'm Michael Chen, your business mentor specializing in AI strategy and entrepreneurship. I'm here to help you understand how AI can transform businesses and create opportunities.",
        "sys_prompt_summary": "You are Michael Chen, a successful AI entrepreneur and business strategist. You help people understand the business side of AI, from strategy to implementation and scaling.",
    }


def get_sample_conversation_data() -> List[Dict[str, str]]:
    """
    Get sample conversation data for testing.
    
    Returns:
        List of conversation messages
    """
    return [
        {"role": "user", "content": "Hello! I want to learn about AI and machine learning."},
        {"role": "assistant", "content": "Great! I'd be happy to help you learn about AI and machine learning. What specific area interests you most? Are you looking to understand the fundamentals, or do you have a particular application in mind?"},
        {"role": "user", "content": "I'm interested in understanding the fundamentals first. What are the main types of machine learning?"},
        {"role": "assistant", "content": "Excellent question! There are three main types of machine learning:\n\n1. **Supervised Learning**: Uses labeled training data to learn patterns. Examples include image classification, spam detection, and price prediction.\n\n2. **Unsupervised Learning**: Finds patterns in data without labels. Examples include clustering customers, anomaly detection, and dimensionality reduction.\n\n3. **Reinforcement Learning**: Learns through trial and error with rewards/penalties. Examples include game playing AI, robotics, and autonomous vehicles.\n\nWhich of these sounds most interesting to you?"},
        {"role": "user", "content": "Supervised learning sounds most relevant to my work. Can you explain how it works in more detail?"},
        {"role": "assistant", "content": "Absolutely! Supervised learning is like learning with a teacher. Here's how it works:\n\n**The Process:**\n1. You provide the algorithm with many examples of input data and the correct answers (labels)\n2. The algorithm learns patterns from these examples\n3. When given new, unseen data, it can make predictions based on what it learned\n\n**Key Concepts:**\n- **Features**: The input variables (e.g., age, income, location)\n- **Labels**: The correct answers you want to predict (e.g., 'spam' or 'not spam')\n- **Training**: The learning process using historical data\n- **Testing**: Evaluating how well the model performs on new data\n\n**Common Algorithms:**\n- Linear Regression (for continuous values)\n- Decision Trees (easy to understand)\n- Random Forest (robust and accurate)\n- Neural Networks (for complex patterns)\n\nWould you like me to explain any of these algorithms in more detail?"},
    ]


def get_sample_ai_response_data() -> Dict[str, Any]:
    """
    Get sample AI response data for testing.
    
    Returns:
        Dict containing sample AI response data
    """
    return {
        "name": "Dr. Sarah Johnson",
        "mentor_age": 42,
        "background": "Experienced AI researcher with 15+ years in machine learning and neural networks. PhD in Computer Science from MIT, published 50+ papers in top-tier conferences.",
        "recent_events": "Recently published a breakthrough paper on transformer architectures and completed a course on advanced deep learning techniques. Currently working on explainable AI research.",
        "personality_style": "Professional yet approachable, encouraging, patient, and detail-oriented. Loves to break down complex concepts into understandable parts.",
        "greeting": "Hello! I'm Dr. Sarah Johnson, and I'm thrilled to be your AI mentor. I understand you're interested in learning about artificial intelligence and machine learning. What specific area would you like to explore first?",
        "sys_prompt_summary": "You are Dr. Sarah Johnson, an experienced AI researcher and mentor with deep expertise in machine learning, neural networks, and AI applications. You're friendly, encouraging, and have a talent for making complex topics accessible.",
        "brief_background": "Software developer with 5 years of experience in web development",
        "goal": "Learn AI and machine learning to transition into AI engineering",
    }


def get_sample_embedding_data() -> List[float]:
    """
    Get sample embedding data for testing.
    
    Returns:
        List of float values representing an embedding vector
    """
    return [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0] * 10  # 100-dimensional vector


def get_sample_config_data() -> Dict[str, Any]:
    """
    Get sample configuration data for testing.
    
    Returns:
        Dict containing sample configuration data
    """
    return {
        "common": {
            "bot_token": "test_bot_token",
            "admins": [123456789, 987654321],
            "encryption_key": "test_encryption_key_32_characters_long",
            "encryption_on": True,
        },
        "redis": {
            "use_redis": False,
            "host": "localhost",
            "port": 6379,
            "password": "",
        },
        "postgres": {
            "host": "localhost",
            "port": 5432,
            "user": "test_user",
            "password": "test_password",
            "db": "test_db",
            "enable_logging": False,
        },
        "provider_config": {
            "token": "test_provider_token",
            "currency": "RUB",
            "price": 10000,  # 100 rubles in kopecks
            "mentor_price": 5000,  # 50 rubles in kopecks
            "enabled": True,
        },
    }


def create_sample_user(session, **kwargs) -> DBUser:
    """
    Create a sample user in the database.
    
    Args:
        session: Database session
        **kwargs: Additional user data to override defaults
        
    Returns:
        DBUser: Created user instance
    """
    user_data = get_sample_user_data()
    user_data.update(kwargs)
    
    user = DBUser(**user_data)
    session.add(user)
    session.commit()
    session.refresh(user)
    
    return user


def create_sample_mentor(session, user_id: int, **kwargs) -> DBMentor:
    """
    Create a sample mentor in the database.
    
    Args:
        session: Database session
        user_id: ID of the user who owns this mentor
        **kwargs: Additional mentor data to override defaults
        
    Returns:
        DBMentor: Created mentor instance
    """
    mentor_data = get_sample_mentor_data()
    mentor_data.update(kwargs)
    mentor_data["user_id"] = user_id
    
    mentor = DBMentor(**mentor_data)
    session.add(mentor)
    session.commit()
    session.refresh(mentor)
    
    return mentor


def create_sample_conversation(session, user_id: int, mentor_id: int = None) -> List[DBConversationMessage]:
    """
    Create sample conversation messages in the database.
    
    Args:
        session: Database session
        user_id: ID of the user
        mentor_id: ID of the mentor (optional)
        
    Returns:
        List[DBConversationMessage]: Created conversation messages
    """
    conversation_data = get_sample_conversation_data()
    messages = []
    
    for msg_data in conversation_data:
        message = DBConversationMessage(
            user_id=user_id,
            mentor_id=mentor_id,
            role=msg_data["role"],
            content=msg_data["content"],
        )
        session.add(message)
        messages.append(message)
    
    session.commit()
    
    for message in messages:
        session.refresh(message)
    
    return messages