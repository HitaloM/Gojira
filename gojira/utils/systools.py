# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

import asyncio


class ShellExceptionError(Exception):
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

    msg = (
        f"Command '{command}' exited with {process.returncode}:\n{stderr.decode("utf-8").strip()}"
    )
    raise ShellExceptionError(msg)
