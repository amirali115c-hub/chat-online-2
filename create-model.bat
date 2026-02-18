@echo off
REM Run this in a terminal where Ollama is installed
ollama create llama3.2-creative -f "%~dp0Modelfile"
pause
