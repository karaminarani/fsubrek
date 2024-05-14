import asyncio

from pyrogram.errors import RPCError
from pyrogram.filters import command
from pyrogram.filters import private
from pyrogram.filters import regex
from pyrogram.handlers import CallbackQueryHandler
from pyrogram.handlers import MessageHandler
from pyrogram.helpers import ikb
from pyrogram.types import CallbackQuery
from pyrogram.types import Message

from .helpers import Filter
from .helpers import helpers
from .helpers import Markup
from bot.client import Bot


@Filter.Admins
async def configs(_, message: Message):
    await message.reply(
        'Bot Configuration Menu:',
        reply_markup=ikb(Markup.HOME),
    )
    await message.delete()


@Filter.Admins
async def cbqhome(client: Bot, cbq: CallbackQuery):
    data = cbq.data.split('-')[1]
    if data == 'close':
        await cbq.message.delete()
    elif data == 'home':
        await cbq.message.edit(
            'Configuration:',
            reply_markup=ikb(Markup.HOME),
        )
    elif data == 'stats':
        await cbq.message.edit(
            'Monitor and Stats:',
            reply_markup=ikb(Markup.STATS),
        )


@Filter.Admins
async def cbqset(client: Bot, cbq: CallbackQuery):
    bvar = client.var.vars
    data = cbq.data.split('-')[1]
    if data == 'admnids':
        admns = bvar.get('ADMIN_IDS', [])
        alist = 'List Admin IDs:\n'
        for i, admn in enumerate(admns):
            alist += f'  {i + 1}. `{admn}`\n'
        await cbq.message.edit(
            alist,
            reply_markup=ikb(Markup.SET_ADMIN),
        )
    elif data == 'fscids':
        fsubs = bvar.get('FSUB_IDS', [])
        flist = 'List FSub IDs:\n'
        if fsubs:
            for i, fsub, in enumerate(fsubs):
                flist += f'  {i + 1}. `{fsub}`\n'
        else:
            flist += '  `None`'
        await cbq.message.edit(
            flist,
            reply_markup=ikb(Markup.SET_FSUB),
        )
    elif data == 'prtctcntnt':
        await cbq.message.edit(
            'Protect Content: '
            f"{bvar.get('PROTECT_CONTENT', [])[0]}",
            reply_markup=ikb(Markup.SET_PROTECT),
        )
    elif data == 'gen':
        await cbq.message.edit(
            'Generator: '
            f"{bvar.get('GEN_STATUS', [])[0]}",
            reply_markup=ikb(Markup.SET_GENERATOR),
        )
    elif data == 'strtmsg':
        await cbq.message.edit(
            'Start Text:\n'
            f"  `{bvar.get('START_MESSAGE', [])[0]}`",
            reply_markup=ikb(Markup.SET_START),
        )
    elif data == 'frcmsg':
        await cbq.message.edit(
            'Force Text:\n'
            f"  `{bvar.get('FORCE_MESSAGE', [])[0]}`",
            reply_markup=ikb(Markup.SET_FORCE),
        )


@Filter.Admins
async def cbqchange(client: Bot, cbq: CallbackQuery):
    async def outv(field):
        await client.mdb.outvars(
            'BOT_VARS',
            field,
        )

    async def inv(field, newkey):
        await client.mdb.invar(
            'BOT_VARS',
            field,
            newkey,
        )

    async def replace(field, newkey):
        await outv(field)
        await inv(field, newkey)
        await client.var.fetching()
        await helpers.cached()

    bvar = client.var.vars
    data = cbq.data.split('-')[1]
    if data in ['prtctcntnt', 'gen']:
        status = bvar.get(
            'PROTECT_CONTENT' if data == 'prtctcntnt'
            else 'GEN_STATUS', 
            []
        )[0]
        await replace(
            'PROTECT_CONTENT' if data == 'prtctcntnt'
            else 'GEN_STATUS',
            False if status else True,
        )
        await cbq.message.edit(
            'Protect Content Changed' if data == 'prtctcntnt'
            else 'Generator Changed',
            reply_markup=ikb(Markup.BACK),
        )
    elif data in ['strtmsg', 'frcmsg']:
        await cbq.message.edit(
            'Send '
            f'{"Start" if data == "strtmsg" else "Force"}'
            ' Text',
        )
        listen = await client.listen(
            user_id=cbq.message.chat.id,
        )
        await listen.delete()
        if listen and not listen.text:
            return await cbq.message.edit(
                'Invalid! Just Send a Text',
                reply_markup=ikb(Markup.SET_START),
            )
        await replace(
            'START_MESSAGE' if data == 'strtmsg'
            else 'FORCE_MESSAGE',
            listen.text,
        )
        await cbq.message.edit(
            f'{"Start" if data == "strtmsg" else "Force"} '
            f'Text:\n  `{listen.text}`',
            reply_markup=ikb(Markup.BACK),
        )


@Filter.Admins
async def cbqadd(client: Bot, cbq: CallbackQuery):
    async def addvar(field, newkey):
        await client.mdb.invar(
            'BOT_VARS',
            field,
            newkey,
        )
        await client.var.fetching()
        await helpers.cached()

    bvar = client.var.vars
    data = cbq.data.split('-')[1]
    enti = 'Admin' if data == 'admnids' else 'FSub'
    vari = 'ADMIN_IDS' if data == 'admnids' else 'FSUB_IDS'
    await cbq.message.edit(
        f'Send {"User" if enti == "Admin" else "Chat"} ID '
        f'to Add {enti}',
    )
    listen = await client.listen(
        user_id=cbq.message.chat.id,
    )
    await listen.delete()
    if listen and not listen.text:
        return await cbq.message.edit(
            'Invalid! Just Send a '
            f'{"User" if enti == "Admin" else "Chat"} ID',
            reply_markup=ikb(
                Markup.SET_ADMIN if data == 'admnids'
                else Markup.SET_FSUB,
            ),
        )
    try:
        entiid = int(listen.text)
    except ValueError:
        return await cbq.message.edit(
            'Invalid! Just Send a '
            f'{"User" if enti == "Admin" else "Chat"} ID',
            reply_markup=ikb(
                Markup.SET_ADMIN if data == 'admnids'
                else Markup.SET_FSUB,
            ),
        )
    if entiid in bvar.get(vari, []):
        return await cbq.message.edit(
            f'{"User" if enti == "Admin" else "Chat"} ID '
            'Already Exists',
            reply_markup=ikb(
                Markup.SET_ADMIN if data == 'admnids'
                else Markup.SET_FSUB,
            ),
        )
    await cbq.message.edit('Initializing...')
    try:
        if data == 'admnids':
            await client.get_users(entiid)
        else:
            (await client.get_chat(entiid)).invite_link
    except RPCError:
        return await cbq.message.edit(
            'Invalid! '
            f'{"User" if enti == "Admin" else "Chat"} ID '
            'Not Found',
            reply_markup=ikb(
                Markup.SET_ADMIN if data == 'admnids'
                else Markup.SET_FSUB,
            ),
        )
    await addvar(vari, entiid)
    await cbq.message.edit(
        f'Added {enti}: `{entiid}`',
        reply_markup=ikb(Markup.BACK),
    )


@Filter.Admins
async def cbqdel(client: Bot, cbq: CallbackQuery):
    async def delvar(field, newkey):
        await client.mdb.rmvar(
            'BOT_VARS',
            field,
            newkey,
        )
        await client.var.fetching()
        await helpers.cached()

    bvar = client.var.vars
    data = cbq.data.split('-')[1]
    enti = 'Admin' if data == 'admnids' else 'FSub'
    vari = 'ADMIN_IDS' if data == 'admnids' else 'FSUB_IDS'
    await cbq.message.edit(
        f'Send {enti} ID to Delete {enti}',
    )
    listen = await client.listen(
        user_id=cbq.message.chat.id,
    )
    await listen.delete()
    if listen and not listen.text:
        return await cbq.message.edit(
            'Invalid! Just Send a '
            f'{"User" if enti == "Admin" else "Chat"} ID',
            reply_markup=ikb(
                Markup.SET_ADMIN if data == 'admnids'
                else Markup.SET_FSUB,
            ),
        )
    try:
        entiid = int(listen.text)
    except ValueError:
        return await cbq.message.edit(
            'Invalid! Just Send a '
            f'{"User" if enti == "Admin" else "Chat"} ID',
            reply_markup=ikb(
                Markup.SET_ADMIN if data == 'admnids'
                else Markup.SET_FSUB,
            ),
        )
    if entiid not in bvar.get(vari, []):
        return await cbq.message.edit(
            'Invalid! '
            f'{"User" if enti == "Admin" else "Chat"} ID '
            'Not Found',
            reply_markup=ikb(
                Markup.SET_ADMIN if data == 'admnids'
                else Markup.SET_FSUB,
            ),
        )
    if entiid == cbq.message.chat.id:
        return await cbq.message.edit(
            "No Rights! That's You",
            reply_markup=ikb(
                Markup.SET_ADMIN if data == 'admnids'
                else Markup.SET_FSUB,
            ),
        )
    await delvar(vari, entiid)
    await cbq.message.edit(
        f'Deleted {enti}: `{entiid}`',
        reply_markup=ikb(Markup.BACK),
    )


Bot.add_handler(
    MessageHandler(
        configs,
        filters=command(Bot.cmd.configs) & private,
    ),
)
Bot.add_handler(
    CallbackQueryHandler(
        cbqhome,
        filters=regex(r'^home')
    ),
)
Bot.add_handler(
    CallbackQueryHandler(
        cbqset,
        filters=regex(r'^set'),
    ),
)
Bot.add_handler(
    CallbackQueryHandler(
        cbqchange,
        filters=regex(r'^change'),
    ),
)
Bot.add_handler(
    CallbackQueryHandler(
        cbqadd,
        filters=regex(r'^add'),
    ),
)
Bot.add_handler(
    CallbackQueryHandler(
        cbqdel,
        filters=regex(r'^del'),
    ),
)
