deactivate
CD build_env

COPY /y ..\pyproject.toml .\
COPY /y ..\poetry.lock .\

RMDIR /s /q .venv
poetry install --only main

CD ..

RMDIR /s /q dist
MKDIR dist\cnf
COPY /y src\cnf\defaults.toml dist\cnf\
COPY /y src\cnf\logging.toml dist\cnf\

poetry build

for /f "usebackq delims=" %%A in (`dir /b dist\autobackup-*.whl`) do set WHL_FILE=%%A

CALL build_env\.venv\Scripts\activate.bat & pip install dist\%WHL_FILE% & pyinstaller src\main.py --name autobackup --onefile --clean & deactivate