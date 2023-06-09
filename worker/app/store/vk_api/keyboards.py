import json


def create_start_keyboard():
    return json.dumps(
        {
            "inline": True,
            "buttons": [
                [
                    {
                        "action": {
                            "type": "callback",
                            "payload": '{"callback_data": "recruiting_started"}',
                            "label": "Начать набор участников",
                        },
                        "color": "primary",
                    },
                ],
                [
                    {
                        "action": {
                            "type": "callback",
                            "payload": '{"callback_data": "check_leaderboard"}',
                            "label": "Посмотреть таблицу лидеров",
                        },
                        "color": "primary",
                    },
                ],
            ],
        }
    )


def create_new_poll_keyboard(variants: list[dict]):
    return json.dumps(
        {
            "inline": True,
            "buttons": [
                [
                    {
                        "action": {
                            "type": "callback",
                            "payload": '{"callback_data": '
                            + f'"vk_id: {variants[0]["vk_id"]}"'
                            + "}",
                            "label": f"{variants[0]['name']} (Голосов: {variants[0]['score']})",
                        },
                        "color": "primary",
                    },
                ],
                [
                    {
                        "action": {
                            "type": "callback",
                            "payload": '{"callback_data": '
                            + f'"vk_id: {variants[1]["vk_id"]}"'
                            + "}",
                            "label": f"{variants[1]['name']} (Голосов: {variants[1]['score']})",
                        },
                        "color": "primary",
                    },
                ],
                [
                    {
                        "action": {
                            "type": "callback",
                            "payload": '{"callback_data": "end game"}',
                            "label": "Досрочно закончить игру",
                        },
                        "color": "negative",
                    },
                ],
            ],
        }
    )


def create_recruiting_keyboard():

    return json.dumps(
        {
            "inline": True,
            "buttons": [
                [
                    {
                        "action": {
                            "type": "callback",
                            "payload": '{"callback_data": "add me"}',
                            "label": "Хочу участвовать",
                        },
                        "color": "primary",
                    },
                ],
                [
                    {
                        "action": {
                            "type": "callback",
                            "payload": '{"callback_data": "delete me"}',
                            "label": "Больше не хочу участвовать",
                        },
                        "color": "primary",
                    },
                ],
                [
                    {
                        "action": {
                            "type": "callback",
                            "payload": '{"callback_data": "start games"}',
                            "label": "Начать игру",
                        },
                        "color": "positive",
                    },
                ],
                [
                    {
                        "action": {
                            "type": "callback",
                            "payload": '{"callback_data": "delete games"}',
                            "label": "Отменить игру",
                        },
                        "color": "negative",
                    },
                ],
            ],
        }
    )
