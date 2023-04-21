# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022-2023 Hitalo M. <https://github.com/HitaloM>

from typing import Any, Dict, Optional, cast

from aiogram.types import TelegramObject, User
from aiogram.utils.i18n import I18nMiddleware
from babel import Locale, UnknownLocaleError

from gojira.database.models import Users


class MyI18nMiddleware(I18nMiddleware):
    async def get_locale(self, event: TelegramObject, data: Dict[str, Any]) -> str:
        user: Optional[User] | Optional[Users] = data.get("event_from_user", None)

        if user is None or user.language_code is None:
            return self.i18n.default_locale

        user = await Users.get_or_none(id=user.id)
        if user is None:
            return self.i18n.default_locale

        try:
            locale = Locale.parse(user.language_code, sep="-")
        except UnknownLocaleError:
            return self.i18n.default_locale

        if locale.language not in self.i18n.available_locales:
            return self.i18n.default_locale
        return cast(str, locale.language)
