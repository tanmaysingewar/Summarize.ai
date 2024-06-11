## To run a server locally you must have Python 3 and UV installed
and follow the below instructions for the setup

### Create the env with uv
```bash
uv venv
```


### Activate the virtual environment:
```bash
source .venv/bin/activate
```

### To install a package into the virtual environment:
#### All the packages are mentioned in the requirements.txt files 
```bash
uv pip install -r requirements.txt
```

### Run Sever
```bash
fastapi dev main.py
```

### Deactivate 
```bash
deactivate
```