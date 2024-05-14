import asyncio
import contextlib
import time

from pyrogram.errors import FloodWait
from pyrogram.errors import RPCError
from pyrogram.filters import command
from pyrogram.filters import create
from pyrogram.filters import private
from pyrogram.filters import regex
from pyrogram.handlers import CallbackQueryHandler
from pyrogram.handlers import MessageHandler
from pyrogram.helpers import ikb
from pyrogram.raw.functions import Ping
from pyrogram.types import CallbackQuery
from pyrogram.types import Message

from .helpers import Filter
from .helpers import helpers
from .helpers import Markup
from bot.client import Bot


gVarBcRun = False
gVarBcSent = 0
gVarBcFail = 0
gVarBcTotal = 0


@Filter.Admins
async def broadcast(client: Bot, message: Message):
    async def progress(msg):
        global gVarBcSent
        global gVarBcFail
        global gVarBcTotal

        with contextlib.suppress(RPCError):
            await msg.edit(
                'Broadcast Status:\n'
                f' - Sent: {gVarBcSent}/{gVarBcTotal}\n'
                f' - Failed: {gVarBcFail}',
                reply_markup=ikb(Markup.BROADCAST_STATS),
            )

    global gVarBcRun
    global gVarBcSent
    global gVarBcFail
    global gVarBcTotal

    if not (bcmsg := message.reply_to_message):
        return await message.reply(
            'Reply to message.',
            quote=True,
        )

    if gVarBcRun:
        return await message.reply(
            'Currently broadcast is running.',
            quote=True,
        )

    msg = await message.reply(
        'Broadcasting...',
        quote=True,
        reply_markup=ikb(Markup.BROADCAST_STATS),
    )

    await client.mdb.inmsg('bmsg', message.chat.id, msg.id)

    users = await client.mdb.gusrs()
    admns = helpers.adminids
    users = [usr for usr in users if usr not in admns]

    gVarBcRun = True
    gVarBcSent = 0
    gVarBcFail = 0
    gVarBcTotal = len(users)

    client.log.info('Starting Broadcast')
    for usr in users:
        if not gVarBcRun:
            break
        try:
            await helpers.copymsgs(bcmsg, usr)
            gVarBcSent += 1
        except FloodWait as e:
            await asyncio.sleep(e.value)
            client.log.warning(str(e))
        except RPCError:
            await client.mdb.rmusr(usr)
            gVarBcFail += 1
        if gVarBcSent + gVarBcFail % 150 == 0:
            asyncio.create_task(progress(msg))

    if gVarBcSent + gVarBcFail == gVarBcTotal:
        await msg.delete()

    await message.reply(
        f'Sent: {gVarBcSent}/{gVarBcTotal}\n'
        f'Failed: {gVarBcFail}',
        quote=True,
        reply_markup=ikb([[('Close', 'home-close')]]),
    )

    gVarBcRun = False
    gVarBcSent = 0
    gVarBcFail = 0
    gVarBcTotal = 0

    client.log.info('Broadcast Finished')

    await client.mdb.rmmsg('bmsg')


async def cbqbcstats(client: Bot, cbq: CallbackQuery):
    global gVarBcRun
    global gVarBcSent
    global gVarBcFail
    global gVarBcTotal

    data = cbq.data.split('-')[1]
    if data == 'refresh':
        with contextlib.suppress(RPCError):
            await cbq.message.edit(
                'Broadcast Status:\n'
                f' - Sent: {gVarBcSent}/{gVarBcTotal}\n'
                f' - Failed: {gVarBcFail}',
                reply_markup=ikb(Markup.BROADCAST_STATS),
            )
    elif data == 'abort':
        await client.mdb.rmmsg('bmsg')
        gVarBcRun = False
        await cbq.message.edit(
            'Broadcast Aborted!',
            reply_markup=ikb([[('Close', 'home-close')]]),
        )


@Filter.Admins
async def cbqstats(client: Bot, cbq: CallbackQuery):
    global gVarBcRun
    global gVarBcSent
    global gVarBcFail
    global gVarBcTotal

    users = await client.mdb.gusrs()
    data = cbq.data.split('-')[1]
    if data == 'ping':
        start = time.time()
        await client.invoke(Ping(ping_id=0))
        laten = f'{(time.time() - start) * 1000:.2f}ms'
        await cbq.answer(f'Pong! {laten}', show_alert=True)
    if data == 'users':
        await cbq.answer(
            f'Total: {len(users)} Users',
            show_alert=True,
        )
    if data == 'bc':
        if not gVarBcRun:
            return await cbq.answer(
                'No Broadcast is Running!',
                show_alert=True,
            )
        Broadcast = \
            f'Broadcast Status:\n' \
            f' - Sent: {gVarBcSent}/{gVarBcTotal}\n' \
            f' - Failed: {gVarBcFail}'
        await cbq.answer(Broadcast, show_alert=True)


ChatTypeGROUP = create(
    lambda _, __,
    message: message.chat.type.value == 'group',
)

Bot.add_handler(
    MessageHandler(
        broadcast,
        filters=command(Bot.cmd.broadcast) &
        ~ChatTypeGROUP,
    ),
)
Bot.add_handler(
    CallbackQueryHandler(
        cbqbcstats,
        filters=regex(r'^bc')
    ),
)
Bot.add_handler(
    CallbackQueryHandler(
        cbqstats,
        filters=regex(r'^stats'),
    ),
)
