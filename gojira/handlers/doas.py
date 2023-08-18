# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

import datetime
import html
import io
import os
import shutil
import sys
import traceback
from pathlib import Path
from signal import SIGINT

import aiofiles
import humanize
import msgspec
from aiogram import F, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import BufferedInputFile, CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from meval import meval

from gojira import cache, i18n
from gojira.database import DB_PATH, Chats, Users
from gojira.filters.user_status import IsSudo
from gojira.utils.callback_data import StartCallback
from gojira.utils.systools import ShellExceptionError, parse_commits, shell_run

router = Router(name="doas")

# Only sudo users can use these commands
router.message.filter(IsSudo())
router.callback_query.filter(IsSudo())


@router.message(Command("errtest"))
async def error_test(message: Message):
    await message.reply("Testing error handler...")
    test = 2 / 0
    print(test)


@router.message(Command("purgecache"))
async def purge_cache(message: Message):
    start = datetime.datetime.now(tz=datetime.UTC)
    await cache.clear()
    delta = (datetime.datetime.now(tz=datetime.UTC) - start).total_seconds() * 1000
    await message.reply(f"Cache purged in <code>{delta:.2f}ms</code>.")


@router.message(Command("event"))
async def json_dump(message: Message):
    event = str(msgspec.json.encode(str(message)).decode())
    await message.reply(event)


@router.message(Command(commands=["doc", "upload"]))
async def upload_document(message: Message, command: CommandObject):
    path = Path(str(command.args))
    if not Path.exists(path):
        await message.reply("File not found.")
        return

    await message.reply("Processing...")

    caption = f"<b>File:</b> <code>{path.name}</code>"
    async with aiofiles.open(path, "rb") as f:
        file_data = await f.read()
        file_obj = BufferedInputFile(file_data, filename=path.name)
        await message.reply_document(file_obj, caption=caption)


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
    except ShellExceptionError as error:
        await sent.edit_text(f"<code>{html.escape(str(error))}</code>")
        return

    commits = parse_commits(stdout)
    changelog = "<b>Changelog</b>:\n"
    for c_hash, commit in commits.items():
        changelog += f"  - [<code>{c_hash[:7]}</code>] {html.escape(commit['title'])}\n"
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

    commands = [
        "git reset --hard origin/main",
        "pybabel compile -d locales -D bot",
        "pip install -U .",
    ]

    stdout = ""
    for command in commands:
        try:
            stdout += await shell_run(command)
        except ShellExceptionError as error:
            await sent.edit_text(f"<code>{html.escape(str(error))}</code>")
            return

    await sent.reply("Uploading logs...")
    document = io.BytesIO(stdout.encode())
    document.name = "update_log.txt"
    document = BufferedInputFile(document.getvalue(), filename=document.name)
    await sent.reply_document(document=document)

    await sent.reply("Restarting...")
    os.execv(sys.executable, [sys.executable, "-m", "gojira"])


@router.message(Command(commands=["shell", "sh"]))
async def bot_shell(message: Message, command: CommandObject):
    code = str(command.args)
    sent = await message.reply("Running...")

    try:
        stdout = await shell_run(command=code)
    except ShellExceptionError as error:
        await sent.edit_text(f"<code>{html.escape(str(error))}</code>")
        return

    output = f"<b>Input\n&gt;</b> <code>{code}</code>\n\n"
    if stdout:
        if len(stdout) > (4096 - len(output)):
            document = io.BytesIO(stdout.encode())
            document.name = "output.txt"
            document = BufferedInputFile(document.getvalue(), filename=document.name)
            await message.reply_document(document=document)
        else:
            output += f"<b>Output\n&gt;</b> <code>{html.escape(stdout)}</code>"

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
            traceback.format_exception(exc[0], exc[1], exc[2].tb_next.tb_next.tb_next)  # type: ignore[misc]  # noqa: E501
        )
        error_txt = "<b>Failed to execute the expression:\n&gt;</b> <code>{eval}</code>"
        error_txt += "\n\n<b>Error:\n&gt;</b> <code>{exc}</code>"
        await sent.edit_text(
            error_txt.format(eval=query, exc=html.escape(exc)),
            disable_web_page_preview=True,
        )
        return

    output_message = f"<b>Expression:\n&gt;</b> <code>{html.escape(str(query))}</code>"

    if stdout:
        lines = str(stdout).splitlines()
        output = "".join(f"<code>{html.escape(line)}</code>\n" for line in lines)

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
    start = datetime.datetime.now(tz=datetime.UTC)
    sent = await message.reply("<b>Pong!</b>")
    delta = (datetime.datetime.now(tz=datetime.UTC) - start).total_seconds() * 1000
    await sent.edit_text(f"<b>Pong!</b> <code>{delta:.2f}ms</code>")


@router.message(Command("stats"))
async def bot_stats(message: Message):
    db_size = humanize.naturalsize(Path.stat(DB_PATH).st_size, binary=True)
    text = f"\n<b>Database Size</b>: <code>{db_size}</code>"
    disk = shutil.disk_usage("/")
    text += f"\n<b>Free Storage</b>: <code>{humanize.naturalsize(disk[2], binary=True)}</code>"

    text += f"\n\n<b>Total Users</b>: <code>{await Users.get_users_count()}</code>"
    for language in (*i18n.available_locales, i18n.default_locale):
        users = await Users.get_users_count(language_code=language)
        text += f"\n<b>{language}</b>: <code>{users}</code>"

    text += f"\n\n<b>Total Groups</b>: <code>{await Chats.get_chats_count()}</code>"
    for language in (*i18n.available_locales, i18n.default_locale):
        groups = await Chats.get_chats_count(language_code=language)
        text += f"\n<b>{language}</b>: <code>{groups}</code>"

    await message.reply(text)
