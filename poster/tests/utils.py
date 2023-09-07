from telebot.types import Chat
from telebot.types import User

BOT_TOKEN = '01234567890:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
BOT_INFO = User.de_json({
    'id': 1234567890,
    'is_bot': True,
    'first_name': 'test_bot_1_first_name',
    'username': 'test_fff_test_bot',
    'last_name': None,
    'language_code': None,
    'can_join_groups': True,
    'can_read_all_group_messages': False,
    'supports_inline_queries': False,
    'is_premium': None,
    'added_to_attachment_menu': None,
})

CHANNEL_ID = -1234567890
CHANNEL_INFO = Chat.de_json({
    'id': -1001899403508,
    'type': 'channel',
    'title': 'test cnannel 3\U0001faf5',
    'username': 'cchhaanneell3',
    'first_name': None,
    'last_name': None,
    'is_forum': None,
    'photo': None,
    'bio': None,
    'join_to_send_messages': None,
    'join_by_request': None,
    'has_private_forwards': None,
    'has_restricted_voice_and_video_messages': None,
    'description': 'test cnannel description',
    'invite_link': 'https://t.me/+XXXXXXXXXXXXXX',
    'pinned_message': None,
    'permissions': None,
    'slow_mode_delay': None,
    'message_auto_delete_time': None,
    'has_protected_content': None,
    'sticker_set_name': None,
    'can_set_sticker_set': None,
    'linked_chat_id': None,
    'location': None,
    'active_usernames': ['channel_username'],
    'emoji_status_custom_emoji_id': None,
    'has_hidden_members': None,
    'has_aggressive_anti_spam_enabled': None
})
