# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022-2023 Hitalo M. <https://github.com/HitaloM>

from tortoise import fields
from tortoise.models import Model


class Users(Model):
    id = fields.BigIntField(pk=True)
    language_code = fields.CharField(max_length=255, default="en")


class Chats(Model):
    id = fields.BigIntField(pk=True)
    language_code = fields.CharField(max_length=255, default="en")
