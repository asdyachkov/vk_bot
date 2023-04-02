import asyncio
import os

from app.store.bot.manager import BotManager
from app.web.app import setup_app


async def main():
    app = setup_app(
        config_path=os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "config.yaml"
        )
    )
    manager = BotManager(app)
    await manager.connect()
    while True:
        await manager.handle_updates()


if __name__ == "__main__":
    asyncio.run(main())
