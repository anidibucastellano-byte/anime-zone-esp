@echo off
title Renombrar Audios
cd /d "%~dp0"

echo ========================================
echo    RENOMBRADOR DE PISTAS DE AUDIO
echo ========================================
echo.

REM Agregar MKVToolNix al PATH si existe
if exist "C:\Program Files\MKVToolNix\mkvpropedit.exe" set "PATH=%PATH%;C:\Program Files\MKVToolNix"
if exist "C:\Program Files (x86)\MKVToolNix\mkvpropedit.exe" set "PATH=%PATH%;C:\Program Files (x86)\MKVToolNix"
if exist "%ProgramData%\Microsoft\Windows\Start Menu\Programs\MKVToolNix\mkvpropedit.exe" set "PATH=%PATH%;%ProgramData%\Microsoft\Windows\Start Menu\Programs\MKVToolNix"

REM Agregar FFmpeg al PATH si existe (buscar en ubicaciones comunes)
if exist "C:\ffmpeg\bin\ffprobe.exe" set "PATH=%PATH%;C:\ffmpeg\bin"
if exist "C:\Program Files\ffmpeg\bin\ffprobe.exe" set "PATH=%PATH%;C:\Program Files\ffmpeg\bin"
if exist "C:\Program Files (x86)\ffmpeg\bin\ffprobe.exe" set "PATH=%PATH%;C:\Program Files (x86)\ffmpeg\bin"
if exist "%USERPROFILE%\ffmpeg\bin\ffprobe.exe" set "PATH=%PATH%;%USERPROFILE%\ffmpeg\bin"

echo Iniciando...
python renombrar_audios.py --interactive

pause
