## Using a nginx reverse proxy to serve docker swarm replicas

Sometimes we need to server backend servers behind a nginx reverse proxy. For example when we want to server a Djnago or a Flask application. In this example I want to show how easy is doing that with nginx.

We're going to start with a dummy Flask application.

```python
from flask import Flask
from datetime import datetime

app = Flask(__name__)

@app.get("/")
def home():
    now = datetime.now()
    return f'Hello {now}'
```

The idea is use a nginx reverse proxy to serve the application. We can configure nginx to do that like this:

```nginx configuration
upstream loadbalancer {
    server backend:5000;
}

server {
    server_tokens off;
    client_max_body_size 20M;
    location / {
        proxy_pass http://loadbalancer;
    }
}
```

And finally we can create our docker-compose.yml file. We only need to set up the replicas and the reverse proxy will do the magic.

```yaml
version: '3.6'

services:
  nginx:
    image: nginx:production
    ports:
      - "8080:80"
  backend:
    image: flask:production
    deploy:
      replicas: 3
    command: gunicorn -w 1 app:app -b 0.0.0.0:5000
```

```commandline
(venv) ➜  docker stack services loadbalancer
ID             NAME                    MODE         REPLICAS   IMAGE              PORTS
u5snhg9tysr0   loadbalancer_backend    replicated   3/3        flask:production
4w0bf8msdiq6   loadbalancer_nginx      replicated   1/1        nginx:production   *:8080->80/tcp 
```

As we can see we have 3 replicas behind a nginx reverse proxy. Maybe it's enough for us, but maybe we need to distinguish between the replicas, for example in the logging.

I've changed a little bit our Flask application.

```python
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
```

And of course our docker-compose.yml file.

```yaml
version: '3.6'

services:
  nginx:
    image: nginx:production
    ports:
      - "8080:80"
  backend:
    image: flask:production
    hostname: "backend.{{.Task.Slot}}"
    environment:
      SLOT: "{{.Task.Slot}}"
      ENVIRONMENT: production
    volumes:
      - log:/src/logs
    deploy:
      replicas: 3
    command: gunicorn -c gunicorn.conf.py -w 1 app:app -b 0.0.0.0:5000
volumes:
  log:
    name: 'log-{{.Task.Slot}}'
```

Now we've changed the hostname of the backend service using the slot number (instead of the default hostname). We also pass a SLOT environment variable to the backend service to distinguish between the replicas, if wee need to do it. Maybe you're asking yourself, why the hell we need to do that? The answer ins simple: Working with legacy code is hard and sometimes we need to do very stranger things.
