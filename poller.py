import asyncio
import os

from app.store.vk_api.accessor import VkApiAccessor
from app.web.app import setup_app


async def main():
    app = setup_app(
        config_path=os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "config.yaml"
        )
    )
    vk_api = VkApiAccessor(app)
    await vk_api.connect(app)
    while True:
        await vk_api.poll()


if __name__ == "__main__":
    asyncio.run(main())
