# ManagerPass
NAME
    ManagerPass v1.0 — Password Manager
    Author: Minux123

DESCRIPTION
    A simple and secure password manager with a modern interface.
    All data is stored locally on your computer.

FEATURES
    • 5 interface languages (Russian, English, Turkish, German, Chinese)
    • Master password to protect all entries
    • Strong password generator
    • Weak password detection (1234, qwerty, etc.)
    • Copy login and password separately
    • Export and import all passwords (JSON)
    • Show/hide password
    • System theme (light/dark follows Windows settings)
    • No Python installation required (ready-to-use .exe included)

INSTALLATION
    Run ManagerPass.exe — the program is ready to use.
    No additional installation required.

DATA STORAGE
    • Passwords are saved in Documents folder: passwords.json
    • Master password hash is saved in Documents folder: master.hash
    • Reset key file: master_reset.key

RESET MASTER PASSWORD
    If you forgot your master password:
        1. On the password entry screen, click "Forgot master password?"
        2. A key file is created in the Documents folder
        3. Restart the program — the master password will be removed
        4. Create a new master password on next launch

SYSTEM REQUIREMENTS
    • Windows 10 / Windows 11
    • No additional software required

FILES INCLUDED
    ManagerPass.exe      — ready-to-use program (run this)
    ManagerPass.txt      — source code
    README.txt           — this file
