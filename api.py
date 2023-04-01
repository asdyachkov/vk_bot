import os
import django
from django.core.management import call_command
from django.core.wsgi import get_wsgi_application

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vk_bot_admin.settings")
    django.setup()
    application = get_wsgi_application()
    proccess1 = call_command('runserver', '127.0.0.1:8000')
