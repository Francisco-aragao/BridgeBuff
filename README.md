# BridgeBuff

## Create virtual env (created with 'env_py' name)

python3 -m venv env_py

## Init virtual env

source env_py/bin/activate

## Install requirements

pip install -r requirements.txt

## Update requirements

pip freeze > requirements.txt

## Server

### Init server -> Port 8000 by default

```fastapi dev ./server/server.py```

### Documentation

Docs are generated automatically by FastApi, just need to run ```localhost:8000/docs``` in the browser after running the server

### Make requests

Typing in the browser ```localhost:8000/api/<path_to_the_route>```

## Client

### Run best performance analysis

```python3 ./client/client.py 127.0.0.1 8000 1 output.csv```

### Run best cannon placement analysis
