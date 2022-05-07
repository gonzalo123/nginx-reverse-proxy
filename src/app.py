import logging
from datetime import datetime
import socket
import os
from logging.handlers import TimedRotatingFileHandler

from flask import Flask

handlers = [
    logging.StreamHandler()
]
if os.getenv('ENVIRONMENT') == 'production':
    slot = os.getenv('SLOT')
    log_path = f"./logs/log{os.getenv('SLOT')}.log"

    file_handler = TimedRotatingFileHandler(log_path, backupCount=2)
    file_handler.setLevel(logging.INFO)
    handlers.append(file_handler)

logging.basicConfig(
    format=f'%(asctime)s ({socket.gethostname()}) [%(levelname)s] %(message)s',
    level='INFO',
    handlers=handlers,
    datefmt='%d/%m/%Y %X'),

logger = logging.getLogger(__name__)

app = Flask(__name__)


@app.get("/")
def home():
    now = datetime.now()
    logger.info(f"home {now}")
    return f'Hello {now} from {socket.gethostname()}. Slot: {os.getenv("SLOT")}'
