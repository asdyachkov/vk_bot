import json


def create_start_keyboard():
    return json.dumps({
       "inline":True,
       "buttons":[
          [
             {
                "action":{
                   "type":"callback",
                   "payload":"{\"callback_data\": \"recruiting_started\"}",
                   "label":"Начать набор участников"
                },
                "color":"primary"
             },
          ]
       ]
    })


def create_recruiting_keyboard():
    return json.dumps({
       "inline":True,
       "buttons":[
          [
             {
                "action":{
                   "type":"callback",
                   "payload":"{\"callback_data\": \"add me\"}",
                   "label":"Хочу участвовать"
                },
                "color":"primary"
             },
          ],
          [
             {
                "action":{
                   "type":"callback",
                   "payload":"{\"callback_data\": \"delete me\"}",
                   "label":"Больше не хочу участвовать"
                },
                "color":"primary"
             },
          ],
          [
             {
                "action":{
                   "type":"callback",
                   "payload":"{\"callback_data\": \"start game\"}",
                   "label":"Начать игру"
                },
                "color":"positive"
             },
          ],
          [
             {
                "action":{
                   "type":"callback",
                   "payload":"{\"callback_data\": \"delete game\"}",
                   "label":"Отменить игру"
                },
                "color":"negative"
             },
          ]
       ]
    })