import PyInstaller.__main__

PyInstaller.__main__.run([
    '--onefile',  # Tworzy jeden plik .exe
    '--noconsole',  # Ukrywa konsolę (przydatne dla aplikacji GUI)
    'myscript.py'  # Twój skrypt do skompilowania
])
