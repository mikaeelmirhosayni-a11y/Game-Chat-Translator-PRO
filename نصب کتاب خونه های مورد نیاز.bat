@echo off
title Installing Game Chat Translator PRO...
color 0A
echo.
echo ========================================
echo   🎮 Game Chat Translator PRO
echo   Installing required libraries...
echo ========================================
echo.

echo [1/5] Installing customtkinter...
pip install customtkinter
echo.

echo [2/5] Installing deep-translator...
pip install deep-translator
echo.

echo [3/5] Installing pyautogui...
pip install pyautogui
echo.

echo [4/5] Installing pygetwindow...
pip install pygetwindow
echo.

echo [5/5] Installing keyboard and pynput...
pip install keyboard pynput
echo.

echo ========================================
echo   ✅ Installation Complete!
echo ========================================
echo.
echo You can now run the translator using run.bat
echo.
pause