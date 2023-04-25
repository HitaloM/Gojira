# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

from tortoise import fields
from tortoise.models import Model


class Users(Model):
    id = fields.BigIntField(pk=True)
    language_code = fields.CharField(max_length=255)


class Chats(Model):
    id = fields.BigIntField(pk=True)
    language_code = fields.CharField(max_length=255)
