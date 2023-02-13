deactivate
CD build_env

COPY /y ..\pyproject.toml .\
COPY /y ..\poetry.lock .\

poetry install --only main

CD ..

CALL build_env\.venv\Scripts\activate.bat & pyinstaller src\autobackup\__main__.py --name autobackup --onefile --clean & deactivate