import asyncio

from pyrogram.errors import FloodWait
from pyrogram.errors import RPCError
from pyrogram.filters import command
from pyrogram.filters import private
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message

from .helpers import helpers
from bot.client import Bot


async def start(client: Bot, message: Message):
    user = message.from_user.id
    bttn = await helpers.usrikb(message, user)

    await client.mdb.inusr(user)

    if len(message.command) == 1:
        if user in helpers.adminids:
            await message.reply(
                helpers.startmsg,
                reply_markup=helpers.admikb(),
            )
        else:
            await message.reply(
                helpers.startmsg,
                reply_markup=bttn,
            )
        return await message.delete()

    if await helpers.nojoin(user):
        await message.reply(
            helpers.forcemsg,
            reply_markup=bttn,
        )
        return await message.delete()

    mids = helpers.decode(message.command[1])
    for msg in await helpers.getmsgs(mids):
        try:
            await helpers.copymsgs(msg, user)
        except FloodWait as e:
            await asyncio.sleep(e.value)
            client.log.warning(str(e))
        except RPCError:
            continue
    return await message.delete()


Bot.add_handler(
    MessageHandler(
        start,
        filters=command(Bot.cmd.start) & private,
    ),
)
