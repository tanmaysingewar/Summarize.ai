## Create the env with uv
uv venv

## Activate the virtual environment:
source .venv/bin/activate

## To install a package into the virtual environment:
uv pip install fastapi
uv pip install -r requirements.txt

## Run Sever
fastapi dev main.py

## Deactivate 
deactivate