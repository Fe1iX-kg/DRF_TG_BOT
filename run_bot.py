import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from students.telegram_bot import main

if __name__ == '__main__':
    main()