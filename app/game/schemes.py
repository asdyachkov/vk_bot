from datetime import date

from marshmallow import Schema, fields


class GameDCSchema(Schema):
    created_at = fields.DateTime(default=date.today())
    chat_id = fields.Int(required=True)
    players = fields.Nested("PlayerDCSchema", many=True, required=True)


class PlayerDCSchema(Schema):
    vk_id = fields.Int(required=False)
    name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    score = fields.Nested("GameScoreDCSchema", many=False, required=True)


class GameScoreDCSchema(Schema):
    points = fields.Int(required=True)
