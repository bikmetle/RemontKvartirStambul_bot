import os

from dotenv import load_dotenv

load_dotenv('.env')
# DEV = int(os.environ.get('DEV'))
OWNER = int(os.environ.get('OWNER'))
TOKEN = os.environ.get('TOKEN')
GROUP = os.environ.get('GROUP')
# WEBHOOK_HOST = os.environ.get('WEBHOOK_HOST')
# WEBHOOK_PATH = os.environ.get('WEBHOOK_PATH')
# WEBAPP_HOST = os.environ.get('WEBAPP_HOST')
# PRODUCTION = int(os.environ.get('PRODUCTION'))