from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.db.repositories.conversation import ConversationRepository
from tgbot.db.repositories.mentor import MentorRepository
from tgbot.db.repositories.user import UserRepository


class Repository:
    def __init__(self, session: AsyncSession) -> None:
        self.users = UserRepository(session)
        self.mentors = MentorRepository(session)
        self.conversations = ConversationRepository(session)
