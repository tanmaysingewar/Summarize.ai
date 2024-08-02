## Create the env with uv
uv venv

## Activate the virtual environment:
source .venv/bin/activate

## To install a package into the virtual environment:
uv pip install -r requirements.txt

## run the app
pymon main.py

## Deactivate 
deactivate