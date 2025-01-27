from telethon import TelegramClient
from telethon.tl.types import ChannelParticipantAdmin, ChannelParticipantCreator

from config import BOT_TOKEN

client = TelegramClient('', '', '')

async def get_chat_members(chat_id):
    await client.start(bot_token=BOT_TOKEN)
    chat_members = []
    async for member in client.iter_participants(chat_id):
        if not member.bot and not isinstance(member.participant, (ChannelParticipantAdmin, ChannelParticipantCreator)):
            chat_members.append(str(member.id))
    await client.disconnect()
    return chat_members 
