# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

import os
from importlib import import_module
from pathlib import Path
from types import ModuleType

from aiogram import Dispatcher

from gojira.utils.logging import log

LOADED_MODULES: dict[str, ModuleType] = {}
MODULES: list[str] = []

for root, dirs, files in os.walk(Path(__file__).parent):
    for file in files:
        if file.endswith(".py") and not file.startswith("_"):
            module_path = Path(root) / file
            module_name = (
                module_path.relative_to(Path(__file__).parent)
                .as_posix()[:-3]
                .replace(os.path.sep, ".")
            )
            MODULES.append(module_name)


def load_modules(dp: Dispatcher, to_load: list[str] = ["*"], to_not_load: list[str] = []) -> None:
    log.debug("Importing modules...")
    if "*" in to_load:
        log.debug("Loading all modules...")
        to_load = MODULES
    else:
        log.debug("Loading %s modules...", " ,".join(to_load))

    for module_name in (x for x in MODULES if x in to_load and x not in to_not_load):
        module = import_module(f"gojira.handlers.{module_name}")
        dp.include_router(getattr(module, "router"))
        LOADED_MODULES[module.__name__.split(".", 3)[2]] = module

    log.info("Loaded modules!", modules=", ".join(LOADED_MODULES.keys()))
