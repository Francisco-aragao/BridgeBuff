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

Important: The file will be stored in the path ```../output_data/<output_file>```, so the <outputfile> is just the filename, not a path. The client needs to be executed inside the folder 'client' too.

### Run best performance analysis in terminal

```python3 client.py <ip> <port> 1 <output_file>```

### Run best cannon placement analysis in terminal

```python3 client.py <ip> <port> 2 <output_file>```

### Run Client in web

uvicorn front:app --reload --port <port_number>