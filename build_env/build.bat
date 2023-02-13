deactivate
RMDIR /s /q build_env\.venv

COPY /y pyproject.toml build_env\
COPY /y poetry.lock build_env\

CD build_env

poetry install --only main

CD ..

RMDIR /s /q dist
MKDIR dist\cnf
COPY /y src\cnf\defaults.toml dist\cnf\
COPY /y src\cnf\logging.toml dist\cnf\

CALL build_env\.venv\Scripts\activate.bat & pyinstaller src\main.py --name autobackup --onefile --clean & deactivate