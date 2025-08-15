from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

admin_main_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🎁 Подарить подписку", callback_data="admin_gift_sub")],
        [InlineKeyboardButton(text="⛔ Заблокировать пользователя", callback_data="admin_ban_user")],
        [InlineKeyboardButton(text="✉️ Отправить сообщение", callback_data="admin_direct_message")],
        [InlineKeyboardButton(text="📣 Рассылка", callback_data="admin_broadcast")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton(text="📄 Экспорт пользователей", callback_data="admin_export_users")],
        [InlineKeyboardButton(text="🗂 Экспорт переписок", callback_data="admin_export_conversations")],
    ]
)

