from marshmallow import Schema, fields


class AdminSchema(Schema):
    email = fields.Str(required=True)
    vk_id = fields.Int(required=True)
    password = fields.Str(required=True, load_only=True)


class AdminLoginSchema(Schema):
    email = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)
