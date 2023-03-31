import os
from multiprocessing import Process
import django

from app.web.app import setup_app
from aiohttp.web import run_app

if __name__ == "__main__":
    # запуск админки
    from django.core.management import call_command
    from django.core.wsgi import get_wsgi_application

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vk_bot_admin.settings")
    django.setup()
    application = get_wsgi_application()
    proccess1 = Process(target=call_command, args=('runserver', '127.0.0.1:8000'))

    # запуск приложения
    proccess2 = Process(target=run_app, args=(
        setup_app(
            config_path=os.path.join(
                os.path.dirname(os.path.realpath(__file__)), "config.yaml"
            )
        ),
    ))

    proccess1.start()
    proccess2.start()

    proccess1.join()
    proccess2.join()

