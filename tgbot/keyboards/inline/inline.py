from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from tgbot.texts import (
    MENTORS_BUTTON_TEXT,
    PROFILE_BUTTON_TEXT,
    INVITE_FRIEND_BUTTON_TEXT,
    SETTINGS_BUTTON_TEXT,
    BILLING_BUTTON_TEXT,
)

test_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="test", url="test.com")]],
)


main_menu_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text=MENTORS_BUTTON_TEXT,
                callback_data="mentors",
            ),
        ],
        [
            InlineKeyboardButton(
                text=PROFILE_BUTTON_TEXT,
                callback_data="profile",
            ),
        ],
        [
            InlineKeyboardButton(
                text=INVITE_FRIEND_BUTTON_TEXT,
                callback_data="invite_friend",
            ),
        ],
        [
            InlineKeyboardButton(
                text=SETTINGS_BUTTON_TEXT,
                callback_data="settings",
            ),
        ],
        [
            InlineKeyboardButton(
                text=BILLING_BUTTON_TEXT,
                callback_data="billing",
            ),
        ],
    ]
)
