import PyInstaller.__main__
import shutil
import os

# Очистка предыдущих сборок
if os.path.exists('dist'):
    shutil.rmtree('dist')
if os.path.exists('build'):
    shutil.rmtree('build')

# Параметры сборки
PyInstaller.__main__.run([
    './ip-address-checker/main.py',
    '--onefile',          # Создать один исполняемый файл
    '--windowed',         # Не показывать консоль (для GUI приложений)
    '--icon=app.ico',     # Иконка приложения (необязательно)
    '--name=IpChecker'     # Имя выходного файла
])
