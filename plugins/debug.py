import io
import os
import subprocess

from meval import meval
from pyrogram.filters import command
from pyrogram.filters import private
from pyrogram.filters import user
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message

from bot.client import Bot


async def log(_, message: Message):
    await message.reply_document('log.txt', quote=True)


async def evaluate(client: Bot, message: Message):
    if len(message.command) == 1:
        return await message.reply(
            "<pre language='python'>None</pre>",
            quote=True,
        )

    msg = await message.reply('...', quote=True)

    code = message.text.split(maxsplit=1)[1]
    output = '<b>Output: </b>'
    Bot.log.info(f'Eval-In: {code}')

    evars = {
        'c': client,
        'm': message, 'r': message.reply_to_message,
        'u': (
            message.reply_to_message or message
        ).from_user,
    }

    def _print(*args, **kwargs):
        print_out = io.StringIO()
        print(*args, file=print_out, **kwargs)
        return print_out.getvalue()

    evars['print'] = _print

    try:
        result = await meval(code, globals(), **evars)
        output += f"<pre language='python'>{result}</pre>"
        Bot.log.info(f'Eval-Out: {result}')
    except Exception as e:
        Bot.log.info(f'Eval-Out: {e}')
        return await msg.edit(
            '<b>Output:\n'
            f"</b><pre language='python'>{e}</pre>",
        )

    if len(output) > 4096:
        with open('output.txt', 'w') as w:
            w.write(str(result))

        await message.reply_document(
            'output.txt',
            quote=True,
            reply_to_message_id=message.id,
        )
        os.remove('output.txt')
        return await msg.delete()

    await msg.edit(text=output)


async def restart(client: Bot, message: Message):
    msg = await message.reply('Restarting...')
    await client.mdb.inmsg(
        'rmsg',
        message.chat.id,
        msg.id,
    )
    await message.delete()
    with open('log.txt', 'r+') as w:
        w.truncate(0)
    subprocess.run(['python', 'main.py'])


Bot.add_handler(
    MessageHandler(
        log,
        filters=command(Bot.cmd.log) & private &
        user(Bot.env.OWNER_ID),
    ),
)
Bot.add_handler(
    MessageHandler(
        evaluate,
        filters=command(Bot.cmd.evaluate) & private &
        user(Bot.env.OWNER_ID),
    ),
)
Bot.add_handler(
    MessageHandler(
        restart,
        filters=command(Bot.cmd.restart) & private &
        user(Bot.env.OWNER_ID),
    ),
)
