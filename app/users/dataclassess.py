from dataclasses import dataclass


@dataclass
class ChatUser:
    id: int
    first_name: str
    last_name: str
    deactivated: str
    is_closed: bool
