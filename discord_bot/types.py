

class Channel:
    title: str | None
    description: str | None
    photo: None
    username: None
    guild_id: int | None

    def __init__(self, raw_data: dict) -> None:
        self.title = raw_data.get('name')
        self.description = raw_data.get('topic')
        self.guild_id = raw_data.get('guild_id')


class Message:
    message_id: int | None

    def __init__(self, raw_data: dict) -> None:
        self.message_id = raw_data.get('id')


class User:
    username: str | None

    def __init__(self, raw_data: dict) -> None:
        self.username = raw_data.get('username')
