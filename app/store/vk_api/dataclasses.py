from dataclasses import dataclass


@dataclass
class UpdateObject:
    id: int
    user_id: int
    body: str
    peer_id: int = None


@dataclass
class Update:
    type: str
    object: UpdateObject


@dataclass
class UpdateEventObject:
    user_id: int
    payload: dict
    peer_id: int = None
    event_id: str = None
    conversation_message_id: int = None


@dataclass
class UpdateEvent:
    type: str
    object: UpdateEventObject


@dataclass
class Message:
    user_id: int
    text: str
    peer_id: int = None
    event_id: str = None
    conversation_message_id: int = None
