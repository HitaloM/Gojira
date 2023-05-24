# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

import asyncio
import datetime
import html
import io
import os
import sys
import traceback
from signal import SIGINT

from aiogram import F, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import BufferedInputFile, CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from meval import meval

from gojira.filters.user_status import IsSudo
from gojira.utils.callback_data import StartCallback

router = Router(name="doas")

# Only sudo users can use these commands
router.message.filter(IsSudo())
router.callback_query.filter(IsSudo())


class ShellException(Exception):
    pass


def parse_commits(log: str) -> dict:
    commits = {}
    last_commit = ""
    for line in log.splitlines():
        if line.startswith("commit"):
            last_commit = line.split()[1]
            commits[last_commit] = {}
        elif line.startswith("    "):
            if "title" in commits[last_commit]:
                commits[last_commit]["message"] = line[4:]
            else:
                commits[last_commit]["title"] = line[4:]
        elif ":" in line:
            key, value = line.split(": ", 1)
            commits[last_commit][key] = value
    return commits


async def shell_run(command: str) -> str:
    process = await asyncio.create_subprocess_shell(
        command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()

    if process.returncode == 0:
        return stdout.decode("utf-8").strip()

    raise ShellException(
        f"Command '{command}' exited with {process.returncode}:\n{stderr.decode('utf-8').strip()}"
    )


@router.message(Command(commands=["reboot", "restart"]))
async def reboot(message: Message):
    await message.reply("Rebooting...")
    os.execv(sys.executable, [sys.executable, "-m", "gojira"])


@router.message(Command("shutdown"))
async def shutdown_message(message: Message):
    await message.reply("Turning off...")
    os.kill(os.getpid(), SIGINT)


@router.message(Command(commands=["update", "upgrade"]))
async def bot_update(message: Message):
    sent = await message.reply("Checking for updates...")

    try:
        await shell_run("git fetch origin")
        stdout = await shell_run("git log HEAD..origin/main")
        if not stdout:
            await sent.edit_text("There is nothing to update.")
            return
    except ShellException as error:
        await sent.edit_text(f"<code>{error}</code>")
        return

    commits = parse_commits(stdout)
    changelog = "<b>Changelog</b>:\n"
    for c_hash, commit in commits.items():
        changelog += f"  - [<code>{c_hash[:7]}</code>] {commit['title']}\n"
    changelog += f"\n<b>New commits count</b>: <code>{len(commits)}</code>."

    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="🆕 Update", callback_data=StartCallback(menu="update"))
    await sent.edit_text(changelog, reply_markup=keyboard.as_markup())


@router.callback_query(StartCallback.filter(F.menu == "update"))
async def upgrade_callback(callback: CallbackQuery):
    message = callback.message
    if not message:
        return

    await message.edit_reply_markup()
    sent = await message.reply("Upgrading...")

    try:
        await shell_run("git reset --hard origin/main")
    except ShellException as error:
        await sent.edit_text(f"<code>{error}</code>")
        return

    await sent.edit_text("Restarting...")
    os.execv(sys.executable, [sys.executable, "-m", "gojira"])


@router.message(Command(commands=["shell", "sh"]))
async def bot_shell(message: Message, command: CommandObject):
    code = str(command.args)
    sent = await message.reply("Running...")

    try:
        stdout = await shell_run(command=code)
    except ShellException as error:
        await sent.edit_text(f"<code>{error}</code>")
        return

    output = f"<b>Input\n&gt;</b> <code>{code}</code>\n\n"
    if stdout:
        if len(stdout) > (4096 - len(output)):
            document = io.BytesIO(stdout.encode())
            document.name = "output.txt"
            document = BufferedInputFile(document.getvalue(), filename=document.name)
            await message.reply_document(document=document)
        else:
            output += f"<b>Output\n&gt;</b> <code>{stdout}</code>"

    await sent.edit_text(output)


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
    start = datetime.datetime.utcnow()
    sent = await message.reply("<b>Pong!</b>")
    delta = (datetime.datetime.utcnow() - start).total_seconds() * 1000
    await sent.edit_text(f"<b>Pong!</b> <code>{delta:.2f}ms</code>")
