@echo off

for /f "usebackq delims=" %%A in (`cd`) do set CDIR=%%A
set CDIR=%CDIR:"=""%
set CDIR="%CDIR%"

set WORKROOT=%~dp0
set PRJNAME=%~n0
set EMBEDPY=python-3.11-win

set Path=%WORKROOT%%EMBEDPY%;%Path%

cd /d %WORKROOT%
rem python -m %PRJNAME% %*
python -m %PRJNAME% tmp/autobackup.log
cd /d %CDIR%