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

for root, _dirs, files in os.walk(Path(__file__).parent):
    for file in files:
        if file.endswith(".py") and not file.startswith("_"):
            module_path = Path(root) / file
            module_name = (
                module_path.relative_to(Path(__file__).parent)
                .as_posix()[:-3]
                .replace(os.path.sep, ".")
            )
            MODULES.append(module_name)


def load_modules(
    dp: Dispatcher, to_load: list[str] | None = None, to_not_load: list[str] | None = None
) -> None:
    if to_not_load is None:
        to_not_load = []
    if to_load is None:
        to_load = ["*"]
    log.debug("Importing modules...")
    if "*" in to_load:
        log.debug("Loading all modules...")
        to_load = MODULES
    else:
        log.debug("Loading modules...", loading=" ,".join(to_load))

    for module_name in (x for x in MODULES if x in to_load and x not in to_not_load):
        # The inline help module must be loaded last so that
        # there is no conflict with the inline commands
        if module_name == "inline":
            continue

        module = import_module(f"gojira.handlers.{module_name}")
        dp.include_router(module.router)
        LOADED_MODULES[module.__name__.split(".", 3)[2]] = module

    dp.include_router(import_module("gojira.handlers.inline").router)
    log.info("Loaded modules!", modules=", ".join(LOADED_MODULES.keys()))
