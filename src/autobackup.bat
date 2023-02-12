@echo off

for /f "usebackq delims=" %%A in (`cd`) do set CDIR=%%A
set CDIR=%CDIR:"=""%
set CDIR="%CDIR%"

set WORKROOT=%~dp0
set PRJNAME=%~n0
set EMBEDPY=python-3.10-win

set Path=%WORKROOT%%EMBEDPY%;%Path%

cd /d %WORKROOT%
python -m %PRJNAME% %*
cd /d %CDIR%