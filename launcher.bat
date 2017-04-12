@echo off
:: .env\Scripts\python main.py
for /f %%f in ('dir /s /b "assets"') do start /min TextureRecognize.exe %%f --use-cache --default-weights --finish
