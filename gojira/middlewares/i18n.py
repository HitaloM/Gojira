from typing import Any, Dict, Optional, cast

from aiogram.types import TelegramObject, User
from aiogram.utils.i18n import I18nMiddleware
from babel import Locale, UnknownLocaleError


class MyI18nMiddleware(I18nMiddleware):
    async def get_locale(self, event: TelegramObject, data: Dict[str, Any]) -> str:
        event_from_user: Optional[User] = data.get("event_from_user", None)
        if event_from_user is None or event_from_user.language_code is None:
            return self.i18n.default_locale
        try:
            locale = Locale.parse(event_from_user.language_code, sep="-")
        except UnknownLocaleError:
            return self.i18n.default_locale

        if locale.language not in self.i18n.available_locales:
            return self.i18n.default_locale
        return cast(str, locale.language)
