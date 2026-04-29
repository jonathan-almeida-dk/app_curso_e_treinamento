@echo off
cd /d "%~dp0"

call venv\Scripts\activate

:: tenta matar processos antigos do streamlit
taskkill /f /im python.exe >nul 2>&1

python -m streamlit run app.py --server.address 0.0.0.0 --server.port 8501

pause