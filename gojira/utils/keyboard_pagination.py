# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

import math
from dataclasses import dataclass
from typing import Any, Callable, List

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def default_page_callback(x: int) -> str:
    return str(x)


def default_item_callback(i: Any, pg: int) -> str:
    return f"[{pg}] {i}"


def chunk_list(input: List[Any], size: int) -> List[List[Any]]:
    return [input[i : i + size] for i in range(0, len(input), size)]


@dataclass
class Pagination:
    objects: List[Any]
    page_data: Callable[[int], str] = default_page_callback
    item_data: Callable[[Any, int], str] = default_item_callback
    item_title: Callable[[Any, int], str] = default_item_callback

    def create(
        self, page: int, lines: int = 5, columns: int = 1
    ) -> InlineKeyboardMarkup:
        quant_per_page = lines * columns
        page = max(1, page)
        offset = (page - 1) * quant_per_page
        stop = offset + quant_per_page
        cutted = self.objects[offset:stop]

        total = len(self.objects)
        pages_range = list(range(1, math.ceil(total / quant_per_page) + 1))
        last_page = len(pages_range)

        nav = [
            (
                f"‹ {page-1}"
                if n == page - 1 and not n == 1
                else f"{page+1} ›"
                if n == page + 1 and not n == page
                else "« 1"
                if n == 1 and not n == page
                else f"{last_page} »"
                if n == last_page and not n == page
                else f"· {n} ·"
                if n == page
                else n,
                self.page_data(n),
            )
            for n in pages_range
            if (page <= 3 and 1 <= n <= 3)
            or (page >= last_page - 2 and last_page - 2 <= n <= last_page)
            or (n in {1, page - 1, page, page + 1, last_page})
        ]

        buttons = [
            (self.item_title(item, page), self.item_data(item, page)) for item in cutted
        ]
        kb_lines = chunk_list(buttons, columns)

        if last_page > 1:
            kb_lines.append(nav)

        keyboard_markup = InlineKeyboardBuilder()
        for line in kb_lines:
            keyboard_markup.row(
                *(
                    InlineKeyboardButton(text=button[0], callback_data=button[1])
                    for button in line
                )
            )

        return keyboard_markup.as_markup()
