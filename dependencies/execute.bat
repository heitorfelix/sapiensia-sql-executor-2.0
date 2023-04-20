@echo off
setlocal

rem Ativar ambiente virtual
call venv\Scripts\activate.bat

rem Executar arquivo Python
python app.py

rem Desativar ambiente virtual
deactivate
