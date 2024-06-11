## To run a server locally you must have Python 3 and UV installed
and follow the below instruction for the setup

### Create the env with uv
uv venv

### Activate the virtual environment:
source .venv/bin/activate

### To install a package into the virtual environment:
#### All the packages are mentioned in requirements.txt files 
uv pip install -r requirements.txt

### Run Sever
fastapi dev main.py

### Deactivate 
deactivate