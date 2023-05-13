# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

import datetime
import html
import io
import os
import sys
import traceback
from signal import SIGINT

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import BufferedInputFile, Message
from meval import meval

from gojira.filters.user_status import IsSudo

router = Router(name="doas")
router.message.filter(IsSudo())


@router.message(Command(commands=["reboot", "restart"]))
async def reboot(message: Message):
    await message.reply("Rebooting...")
    args = [sys.executable, "-m", "gojira"]
    os.execv(sys.executable, args)


@router.message(Command("shutdown"), IsSudo())
async def shutdown_message(message: Message):
    await message.reply("Turning off...")
    os.kill(os.getpid(), SIGINT)


@router.message(Command(commands=["eval", "ev"]))
async def evaluate(message: Message, command: CommandObject):
    query = command.args
    sent = await message.reply("Evaluating...")

    try:
        stdout = await meval(query, globals(), **locals())
    except BaseException:
        exc = sys.exc_info()
        exc = "".join(
            traceback.format_exception(exc[0], exc[1], exc[2].tb_next.tb_next.tb_next)  # type: ignore  # noqa: E501
        )
        error_txt = "<b>Failed to execute the expression:\n&gt;</b> <code>{eval}</code>"
        error_txt += "\n\n<b>Error:\n&gt;</b> <code>{exc}</code>"
        await sent.edit_text(
            error_txt.format(eval=query, exc=html.escape(exc)), disable_web_page_preview=True
        )
        return

    output_message = f"<b>Expression:\n&gt;</b> <code>{query}</code>"

    if stdout:
        lines = str(stdout).splitlines()
        output = "".join(f"<code>{line}</code>\n" for line in lines)

        if len(output) > 0:
            if len(output) > (4096 - len(output_message)):
                document = io.BytesIO(
                    (output.replace("<code>", "").replace("</code>", "")).encode()
                )
                document.name = "output.txt"
                document = BufferedInputFile(document.getvalue(), filename=document.name)
                await message.reply_document(document=document)
            else:
                output_message += f"\n\n<b>Result:\n&gt;</b> <code>{output}</code>"

    await sent.edit_text(output_message)


@router.message(Command("ping"))
async def ping(message: Message):
    start = datetime.datetime.now().replace(tzinfo=datetime.UTC)
    sent = await message.reply("<b>Pong!</b>")
    end = datetime.datetime.now().replace(tzinfo=datetime.UTC)
    await sent.edit_text(f"<b>Pong!</b> <code>{(end - start).microseconds / 1000}ms</code>")
