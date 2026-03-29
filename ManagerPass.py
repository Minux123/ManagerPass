import os
import json
import customtkinter as ctk
import locale
import random
import string
import hashlib
import time
from datetime import datetime
from tkinter import filedialog
from cryptography.fernet import Fernet

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")

DATA_FOLDER = os.path.join(os.path.expanduser("~"), "Documents", "ManagerPass")
DATA_FILE = os.path.join(DATA_FOLDER, "passwords.enc")
KEY_FILE = os.path.join(DATA_FOLDER, "key.key")
MASTER_HASH_FILE = os.path.join(DATA_FOLDER, "master.hash")
RESET_KEY_FILE = "master_reset.key"

if not os.path.exists(DATA_FOLDER):
    try:
        os.makedirs(DATA_FOLDER)
    except:
        pass

# ==================== ШИФРОВАНИЕ ====================
def get_or_create_key():
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, 'rb') as f:
            return f.read()
    else:
        key = Fernet.generate_key()
        with open(KEY_FILE, 'wb') as f:
            f.write(key)
        return key

def encrypt_data(data, key):
    f = Fernet(key)
    json_str = json.dumps(data, ensure_ascii=False)
    encrypted = f.encrypt(json_str.encode('utf-8'))
    return encrypted

def decrypt_data(encrypted_data, key):
    f = Fernet(key)
    decrypted = f.decrypt(encrypted_data)
    return json.loads(decrypted.decode('utf-8'))

def load_passwords():
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        key = get_or_create_key()
        with open(DATA_FILE, 'rb') as f:
            encrypted = f.read()
        return decrypt_data(encrypted, key)
    except:
        return {}

def save_passwords(passwords):
    key = get_or_create_key()
    encrypted = encrypt_data(passwords, key)
    with open(DATA_FILE, 'wb') as f:
        f.write(encrypted)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def is_master_set():
    return os.path.exists(MASTER_HASH_FILE)

def verify_master(password):
    if not is_master_set():
        return True
    with open(MASTER_HASH_FILE, 'r') as f:
        saved_hash = f.read().strip()
    return hash_password(password) == saved_hash

def set_master_password(password):
    with open(MASTER_HASH_FILE, 'w') as f:
        f.write(hash_password(password))

def remove_master_password():
    if os.path.exists(MASTER_HASH_FILE):
        os.remove(MASTER_HASH_FILE)

def check_reset_key():
    if os.path.exists(RESET_KEY_FILE):
        os.remove(RESET_KEY_FILE)
        remove_master_password()
        return True
    reset_path = os.path.join(os.path.expanduser("~"), "Documents", "master_reset.key")
    if os.path.exists(reset_path):
        os.remove(reset_path)
        remove_master_password()
        return True
    return False

def create_reset_key():
    reset_path = os.path.join(os.path.expanduser("~"), "Documents", "master_reset.key")
    with open(reset_path, 'w') as f:
        f.write("reset")
    return reset_path

# ==================== СПИСОК СЛАБЫХ ПАРОЛЕЙ ====================
WEAK_PASSWORDS = [
    "1234", "12345", "123456", "1234567", "12345678", "123456789",
    "1111", "11111", "111111", "0000", "00000", "000000",
    "qwerty", "qwerty123", "password", "pass", "admin", "root",
    "123123", "abc123", "password1", "qwe123", "1q2w3e", "1qaz2wsx"
]

def is_weak_password(password):
    password_lower = password.lower()
    if password_lower in WEAK_PASSWORDS:
        return True
    if len(set(password)) <= 3:
        return True
    if password.isdigit() and len(password) <= 6:
        return True
    if password.isalpha() and len(password) <= 6:
        return True
    return False

def generate_strong_password(length=12):
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(random.choice(chars) for _ in range(length))
    return password

# ==================== ПЕРЕВОДЫ ====================
LANGUAGES = {
    "Русский": {
        "title": "Менеджер паролей",
        "settings": "⚙️ Настройки",
        "master_password": "Мастер-пароль",
        "master_enabled": "Включить мастер-пароль",
        "master_disabled": "Выключить мастер-пароль",
        "master_change": "Сменить мастер-пароль",
        "master_forgot": "Забыли мастер-пароль?",
        "master_forgot_help": "Файл-ключ создан. Перезапустите программу.",
        "master_title": "Введите мастер-пароль",
        "master_first": "Создайте мастер-пароль",
        "master_confirm": "Подтвердите пароль",
        "master_mismatch": "Пароли не совпадают",
        "master_wrong": "Неверный мастер-пароль",
        "master_success": "Мастер-пароль установлен!",
        "master_removed": "Мастер-пароль отключён!",
        "master_changed": "Мастер-пароль изменён!",
        "master_blocked": "Слишком много попыток. Подождите {} секунд.",
        "site": "Сайт / Сервис:",
        "login": "Логин:",
        "password": "Пароль:",
        "generate": "🎲 Сгенерировать",
        "add": "➕ Добавить",
        "edit": "✏️ Редактировать",
        "delete": "🗑️ Удалить",
        "saved_passwords": "Сохранённые пароли",
        "search": "Поиск:",
        "clear_search": "Сбросить",
        "empty": "Нет сохранённых паролей",
        "site_header": "Сайт / Сервис",
        "login_header": "Логин",
        "password_header": "Пароль",
        "copy_login": "📋 Логин",
        "copy_password": "📋 Пароль",
        "error_empty_site": "Ошибка",
        "error_empty_site_msg": "Введите название сайта",
        "error_empty_password": "Ошибка",
        "error_empty_password_msg": "Введите пароль",
        "weak_password_warning": "⚠️ Слабый пароль",
        "weak_password_msg": "Пароль слишком простой. Рекомендуется использовать более сложный пароль.",
        "success": "Успех",
        "saved_msg": "Пароль для {} сохранён!",
        "edit_title": "Редактировать",
        "edit_site": "Название сайта:",
        "edit_login": "Логин:",
        "edit_password": "Пароль:",
        "save": "Сохранить",
        "updated_msg": "Запись обновлена!",
        "select_site": "Выберите сайт для редактирования:",
        "select_delete": "Выберите сайт для удаления:",
        "confirm_delete": "Подтверждение",
        "confirm_delete_msg": "Удалить пароль для {}?",
        "deleted_msg": "Пароль для {} удалён!",
        "copied": "Скопировано",
        "copied_login_msg": "Логин для {} скопирован",
        "copied_pass_msg": "Пароль для {} скопирован",
        "language": "🌐 Язык",
        "by_minux": "By Minux",
        "show_password": "Показать пароль",
        "cancel": "Отмена",
        "ok": "OK",
        "export": "📤 Экспорт",
        "import": "📥 Импорт",
        "export_success": "Экспорт выполнен!",
        "export_msg": "Пароли сохранены в файл:",
        "import_success": "Импорт выполнен!",
        "import_msg": "Пароли восстановлены из файла",
        "import_error": "Ошибка импорта",
        "import_error_msg": "Не удалось импортировать файл",
        "theme": "Тема",
        "theme_light": "Светлая",
        "theme_dark": "Тёмная",
        "theme_system": "Системная"
    },
    "English": {
        "title": "Password Manager",
        "settings": "⚙️ Settings",
        "master_password": "Master Password",
        "master_enabled": "Enable master password",
        "master_disabled": "Disable master password",
        "master_change": "Change master password",
        "master_forgot": "Forgot master password?",
        "master_forgot_help": "Key file created. Restart the program.",
        "master_title": "Enter master password",
        "master_first": "Create master password",
        "master_confirm": "Confirm password",
        "master_mismatch": "Passwords do not match",
        "master_wrong": "Wrong master password",
        "master_success": "Master password set!",
        "master_removed": "Master password disabled!",
        "master_changed": "Master password changed!",
        "master_blocked": "Too many attempts. Wait {} seconds.",
        "site": "Site / Service:",
        "login": "Login:",
        "password": "Password:",
        "generate": "🎲 Generate",
        "add": "➕ Add",
        "edit": "✏️ Edit",
        "delete": "🗑️ Delete",
        "saved_passwords": "Saved Passwords",
        "search": "Search:",
        "clear_search": "Clear",
        "empty": "No saved passwords",
        "site_header": "Site / Service",
        "login_header": "Login",
        "password_header": "Password",
        "copy_login": "📋 Login",
        "copy_password": "📋 Password",
        "error_empty_site": "Error",
        "error_empty_site_msg": "Enter site name",
        "error_empty_password": "Error",
        "error_empty_password_msg": "Enter password",
        "weak_password_warning": "⚠️ Weak Password",
        "weak_password_msg": "This password is too simple. Use a stronger password.",
        "success": "Success",
        "saved_msg": "Password for {} saved!",
        "edit_title": "Edit",
        "edit_site": "Site name:",
        "edit_login": "Login:",
        "edit_password": "Password:",
        "save": "Save",
        "updated_msg": "Entry updated!",
        "select_site": "Select site to edit:",
        "select_delete": "Select site to delete:",
        "confirm_delete": "Confirm",
        "confirm_delete_msg": "Delete password for {}?",
        "deleted_msg": "Password for {} deleted!",
        "copied": "Copied",
        "copied_login_msg": "Login for {} copied",
        "copied_pass_msg": "Password for {} copied",
        "language": "🌐 Language",
        "by_minux": "By Minux",
        "show_password": "Show password",
        "cancel": "Cancel",
        "ok": "OK",
        "export": "📤 Export",
        "import": "📥 Import",
        "export_success": "Export completed!",
        "export_msg": "Passwords saved to file:",
        "import_success": "Import completed!",
        "import_msg": "Passwords restored from file",
        "import_error": "Import error",
        "import_error_msg": "Failed to import file",
        "theme": "Theme",
        "theme_light": "Light",
        "theme_dark": "Dark",
        "theme_system": "System"
    }
}

def get_system_language():
    try:
        lang_code = locale.getdefaultlocale()[0]
        if lang_code:
            if lang_code.startswith('ru'):
                return "Русский"
        return "English"
    except:
        return "English"

# ==================== ОСНОВНОЙ КЛАСС ====================
class PasswordManager:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("ManagerPass")
        self.window.geometry("1200x800")
        self.window.minsize(1000, 700)
        
        check_reset_key()
        
        self.current_lang = get_system_language()
        self.lang_data = LANGUAGES[self.current_lang]
        self.current_theme = "system"
        
        self.login_attempts = 0
        self.blocked_until = 0
        
        if not self.authenticate_master():
            self.window.destroy()
            return
        
        self.passwords = load_passwords()
        self.settings_window = None
        self.setup_ui()
        self.refresh_list()
        self.update_ui_texts()
        self.apply_theme()
    
    def authenticate_master(self):
        if not is_master_set():
            return self.create_master_password()
        else:
            return self.verify_master_password()
    
    def create_master_password(self):
        dialog = ctk.CTkToplevel(self.window)
        dialog.title(self.lang_data["master_first"])
        dialog.geometry("400x300")
        dialog.grab_set()
        dialog.transient(self.window)
        
        ctk.CTkLabel(dialog, text=self.lang_data["master_first"], font=("Segoe UI", 14)).pack(pady=15)
        
        pass_entry = ctk.CTkEntry(dialog, show="•", width=250)
        pass_entry.pack(pady=5)
        
        ctk.CTkLabel(dialog, text=self.lang_data["master_confirm"]).pack()
        confirm_entry = ctk.CTkEntry(dialog, show="•", width=250)
        confirm_entry.pack(pady=5)
        
        error_label = ctk.CTkLabel(dialog, text="", text_color="red")
        error_label.pack(pady=5)
        
        result = [False]
        
        def on_ok():
            p1 = pass_entry.get()
            p2 = confirm_entry.get()
            if not p1:
                error_label.configure(text="Введите пароль")
                return
            if p1 != p2:
                error_label.configure(text=self.lang_data["master_mismatch"])
                return
            set_master_password(p1)
            result[0] = True
            dialog.destroy()
        
        def on_cancel():
            result[0] = False
            dialog.destroy()
        
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=15)
        ctk.CTkButton(btn_frame, text=self.lang_data["ok"], command=on_ok, width=100).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text=self.lang_data["cancel"], command=on_cancel, width=100).pack(side="left", padx=10)
        
        pass_entry.bind("<Return>", lambda e: on_ok())
        confirm_entry.bind("<Return>", lambda e: on_ok())
        
        dialog.wait_window()
        return result[0]
    
    def verify_master_password(self):
        # Проверка блокировки при входе в метод
        if time.time() < self.blocked_until:
            remaining = int(self.blocked_until - time.time())
            self.show_message(self.lang_data["master_title"], self.lang_data["master_blocked"].format(remaining))
            return False
        
        dialog = ctk.CTkToplevel(self.window)
        dialog.title(self.lang_data["master_title"])
        dialog.geometry("400x350")
        dialog.grab_set()
        dialog.transient(self.window)
        
        ctk.CTkLabel(dialog, text=self.lang_data["master_title"], font=("Segoe UI", 14)).pack(pady=15)
        
        pass_entry = ctk.CTkEntry(dialog, show="•", width=250)
        pass_entry.pack(pady=10)
        
        error_label = ctk.CTkLabel(dialog, text="", text_color="red")
        error_label.pack(pady=5)
        
        result = [False]
        ok_btn = None
        
        def on_ok():
            # Дополнительная проверка блокировки прямо перед проверкой
            if time.time() < self.blocked_until:
                remaining = int(self.blocked_until - time.time())
                error_label.configure(text=self.lang_data["master_blocked"].format(remaining))
                return
            
            p = pass_entry.get()
            if verify_master(p):
                self.login_attempts = 0
                result[0] = True
                dialog.destroy()
            else:
                self.login_attempts += 1
                remaining = 3 - self.login_attempts
                if self.login_attempts >= 3:
                    self.blocked_until = time.time() + 30
                    error_label.configure(text=self.lang_data["master_blocked"].format(30))
                    if ok_btn:
                        ok_btn.configure(state="disabled")
                    def unblock():
                        if ok_btn:
                            ok_btn.configure(state="normal")
                        error_label.configure(text="")
                        self.login_attempts = 0
                    dialog.after(30000, unblock)
                else:
                    error_label.configure(text=f"{self.lang_data['master_wrong']}. Осталось попыток: {remaining}")
                pass_entry.delete(0, 'end')
        
        def on_forgot():
            try:
                reset_path = create_reset_key()
                error_label.configure(text=f"Файл-ключ создан в:\n{reset_path}\n\n{self.lang_data['master_forgot_help']}", text_color="orange")
            except Exception as e:
                error_label.configure(text=f"Ошибка: {e}", text_color="red")
        
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=10)
        ok_btn = ctk.CTkButton(btn_frame, text=self.lang_data["ok"], command=on_ok, width=100)
        ok_btn.pack(side="left", padx=10)
        
        forgot_btn = ctk.CTkButton(
            btn_frame, 
            text=self.lang_data["master_forgot"], 
            command=on_forgot,
            width=120,
            fg_color="#e67e22",
            hover_color="#f39c12"
        )
        forgot_btn.pack(side="left", padx=10)
        
        pass_entry.bind("<Return>", lambda e: on_ok())
        
        dialog.wait_window()
        return result[0]
    
    def apply_theme(self):
        if self.current_theme == "light":
            ctk.set_appearance_mode("light")
        elif self.current_theme == "dark":
            ctk.set_appearance_mode("dark")
        else:
            ctk.set_appearance_mode("system")
    
    def setup_ui(self):
        self.main_frame = ctk.CTkFrame(self.window)
        self.main_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        top_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        top_frame.pack(fill="x", pady=(0, 10))
        
        self.title_label = ctk.CTkLabel(top_frame, text="", font=("Segoe UI", 24, "bold"))
        self.title_label.pack(side="left")
        
        btn_right_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
        btn_right_frame.pack(side="right")
        
        self.settings_btn = ctk.CTkButton(btn_right_frame, text="", command=self.open_settings, width=100)
        self.settings_btn.pack(side="left", padx=5)
        
        self.export_btn = ctk.CTkButton(btn_right_frame, text="", command=self.export_passwords, width=100)
        self.export_btn.pack(side="left", padx=5)
        
        self.import_btn = ctk.CTkButton(btn_right_frame, text="", command=self.import_passwords, width=100)
        self.import_btn.pack(side="left", padx=5)
        
        self.lang_button = ctk.CTkButton(btn_right_frame, text="", width=100, command=self.change_language)
        self.lang_button.pack(side="left", padx=5)
        
        form_frame = ctk.CTkFrame(self.main_frame)
        form_frame.pack(fill="x", pady=(0, 15))
        
        self.site_label = ctk.CTkLabel(form_frame, text="")
        self.site_label.grid(row=0, column=0, padx=10, pady=8, sticky="w")
        self.site_entry = ctk.CTkEntry(form_frame, width=320, placeholder_text="google.com")
        self.site_entry.grid(row=0, column=1, padx=10, pady=8)
        
        self.login_label = ctk.CTkLabel(form_frame, text="")
        self.login_label.grid(row=1, column=0, padx=10, pady=8, sticky="w")
        self.username_entry = ctk.CTkEntry(form_frame, width=320, placeholder_text="user@example.com")
        self.username_entry.grid(row=1, column=1, padx=10, pady=8)
        
        self.password_label = ctk.CTkLabel(form_frame, text="")
        self.password_label.grid(row=2, column=0, padx=10, pady=8, sticky="w")
        
        password_row = ctk.CTkFrame(form_frame, fg_color="transparent")
        password_row.grid(row=2, column=1, padx=10, pady=8, sticky="w")
        
        self.password_entry = ctk.CTkEntry(password_row, width=200, placeholder_text="••••••••", show="•")
        self.password_entry.pack(side="left", padx=(0, 8))
        
        self.generate_btn = ctk.CTkButton(password_row, text="", width=70, command=self.generate_password)
        self.generate_btn.pack(side="left", padx=(0, 8))
        
        self.show_pass_check = ctk.CTkCheckBox(password_row, text="", command=self.toggle_password_visibility)
        self.show_pass_check.pack(side="left")
        
        btn_frame = ctk.CTkFrame(self.main_frame)
        btn_frame.pack(fill="x", pady=(0, 15))
        
        self.add_btn = ctk.CTkButton(btn_frame, text="", command=self.add_password, width=120)
        self.add_btn.pack(side="left", padx=5)
        
        self.edit_btn = ctk.CTkButton(btn_frame, text="", command=self.edit_password, width=120)
        self.edit_btn.pack(side="left", padx=5)
        
        self.delete_btn = ctk.CTkButton(btn_frame, text="", command=self.delete_password, width=120)
        self.delete_btn.pack(side="left", padx=5)
        
        search_frame = ctk.CTkFrame(self.main_frame)
        search_frame.pack(fill="x", pady=(0, 10))
        
        self.search_label = ctk.CTkLabel(search_frame, text="")
        self.search_label.pack(side="left", padx=5)
        
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="google")
        self.search_entry.pack(side="left", fill="x", expand=True, padx=5)
        self.search_entry.bind("<KeyRelease>", self.on_search)
        
        self.clear_search_btn = ctk.CTkButton(search_frame, text="", command=self.clear_search, width=80)
        self.clear_search_btn.pack(side="left", padx=5)
        
        self.list_label = ctk.CTkLabel(self.main_frame, text="", font=("Segoe UI", 14, "bold"))
        self.list_label.pack(anchor="w", pady=(0, 5))
        
        self.tree_frame = ctk.CTkScrollableFrame(self.main_frame, height=400)
        self.tree_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        footer_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        footer_frame.pack(fill="x", pady=(10, 0))
        
        self.credit_label = ctk.CTkLabel(footer_frame, text="", font=("Segoe UI", 12), text_color="gray")
        self.credit_label.pack(side="right")
    
    def on_search(self, event=None):
        self.refresh_list()
    
    def clear_search(self):
        self.search_entry.delete(0, "end")
        self.refresh_list()
    
    def update_ui_texts(self):
        self.title_label.configure(text=self.lang_data["title"])
        self.settings_btn.configure(text=self.lang_data["settings"])
        self.lang_button.configure(text=f"{self.lang_data['language']} 🌐")
        self.export_btn.configure(text=self.lang_data["export"])
        self.import_btn.configure(text=self.lang_data["import"])
        
        self.site_label.configure(text=self.lang_data["site"])
        self.login_label.configure(text=self.lang_data["login"])
        self.password_label.configure(text=self.lang_data["password"])
        self.generate_btn.configure(text=self.lang_data["generate"])
        self.show_pass_check.configure(text=self.lang_data["show_password"])
        
        self.add_btn.configure(text=self.lang_data["add"])
        self.edit_btn.configure(text=self.lang_data["edit"])
        self.delete_btn.configure(text=self.lang_data["delete"])
        
        self.search_label.configure(text=self.lang_data["search"])
        self.clear_search_btn.configure(text=self.lang_data["clear_search"])
        self.list_label.configure(text=self.lang_data["saved_passwords"])
        
        self.credit_label.configure(text=self.lang_data["by_minux"])
    
    def toggle_password_visibility(self):
        if self.show_pass_check.get() == 1:
            self.password_entry.configure(show="")
        else:
            self.password_entry.configure(show="•")
    
    def generate_password(self):
        password = generate_strong_password()
        self.password_entry.delete(0, "end")
        self.password_entry.insert(0, password)
    
    def check_and_warn_weak_password(self, password):
        if is_weak_password(password):
            warn_dialog = ctk.CTkToplevel(self.window)
            warn_dialog.title(self.lang_data["weak_password_warning"])
            warn_dialog.geometry("350x150")
            warn_dialog.grab_set()
            warn_dialog.transient(self.window)
            
            ctk.CTkLabel(warn_dialog, text=self.lang_data["weak_password_msg"], wraplength=300).pack(pady=20)
            ctk.CTkButton(warn_dialog, text=self.lang_data["ok"], command=warn_dialog.destroy).pack(pady=5)
            return True
        return False
    
    def refresh_list(self, search_term=None):
        for widget in self.tree_frame.winfo_children():
            widget.destroy()
        
        self.passwords = load_passwords()
        
        search_text = self.search_entry.get().strip().lower()
        
        items = self.passwords.items()
        if search_text:
            items = [(s, d) for s, d in items if search_text in s.lower() or search_text in d.get('username', '').lower()]
        
        if not items:
            empty_label = ctk.CTkLabel(self.tree_frame, text=self.lang_data["empty"], text_color="gray")
            empty_label.pack(pady=20)
            return
        
        header = ctk.CTkFrame(self.tree_frame)
        header.pack(fill="x", pady=(0, 5))
        ctk.CTkLabel(header, text=self.lang_data["site_header"], font=("Segoe UI", 12, "bold"), width=350).pack(side="left", padx=5)
        ctk.CTkLabel(header, text=self.lang_data["login_header"], font=("Segoe UI", 12, "bold"), width=300).pack(side="left", padx=5)
        ctk.CTkLabel(header, text=self.lang_data["password_header"], font=("Segoe UI", 12, "bold"), width=250).pack(side="left", padx=5)
        ctk.CTkLabel(header, text="", width=160).pack(side="left")
        
        for site, data in items:
            row = ctk.CTkFrame(self.tree_frame)
            row.pack(fill="x", pady=2)
            
            site_var = ctk.StringVar(value=site)
            site_entry = ctk.CTkEntry(row, textvariable=site_var, width=350)
            site_entry.pack(side="left", padx=5)
            site_entry.bind("<FocusOut>", lambda e, s=site, var=site_var: self.edit_cell(s, "site", var.get()))
            
            login_var = ctk.StringVar(value=data['username'])
            login_entry = ctk.CTkEntry(row, textvariable=login_var, width=300)
            login_entry.pack(side="left", padx=5)
            login_entry.bind("<FocusOut>", lambda e, s=site, var=login_var: self.edit_cell(s, "login", var.get()))
            
            password_var = ctk.StringVar(value=data['password'])
            password_entry = ctk.CTkEntry(row, textvariable=password_var, width=250, show="•")
            password_entry.pack(side="left", padx=5)
            password_entry.bind("<FocusOut>", lambda e, s=site, var=password_var: self.edit_cell(s, "password", var.get()))
            
            btn_frame = ctk.CTkFrame(row, fg_color="transparent")
            btn_frame.pack(side="left", padx=5)
            
            copy_login_btn = ctk.CTkButton(btn_frame, text=self.lang_data["copy_login"], width=70, command=lambda s=site, u=data['username']: self.copy_login(s, u))
            copy_login_btn.pack(side="left", padx=2)
            
            copy_pass_btn = ctk.CTkButton(btn_frame, text=self.lang_data["copy_password"], width=70, command=lambda s=site, p=data['password']: self.copy_password(s, p))
            copy_pass_btn.pack(side="left", padx=2)
    
    def edit_cell(self, site, field, new_value):
        if site in self.passwords:
            if field == "site":
                if new_value != site and new_value:
                    self.passwords[new_value] = self.passwords.pop(site)
                    site = new_value
            elif field == "login":
                self.passwords[site]['username'] = new_value
            elif field == "password":
                self.passwords[site]['password'] = new_value
                self.check_and_warn_weak_password(new_value)
            save_passwords(self.passwords)
            self.refresh_list()
    
    def copy_login(self, site, login):
        self.window.clipboard_clear()
        self.window.clipboard_append(login)
        self.show_message(self.lang_data["copied"], self.lang_data["copied_login_msg"].format(site))
    
    def copy_password(self, site, password):
        self.window.clipboard_clear()
        self.window.clipboard_append(password)
        self.show_message(self.lang_data["copied"], self.lang_data["copied_pass_msg"].format(site))
    
    def add_password(self):
        site = self.site_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not site:
            self.show_message(self.lang_data["error_empty_site"], self.lang_data["error_empty_site_msg"])
            return
        if not password:
            self.show_message(self.lang_data["error_empty_password"], self.lang_data["error_empty_password_msg"])
            return
        
        self.check_and_warn_weak_password(password)
        
        self.passwords[site] = {
            "username": username,
            "password": password,
            "date_added": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        save_passwords(self.passwords)
        
        self.site_entry.delete(0, "end")
        self.username_entry.delete(0, "end")
        self.password_entry.delete(0, "end")
        
        self.refresh_list()
        self.show_message(self.lang_data["success"], self.lang_data["saved_msg"].format(site))
    
    def edit_password(self):
        if not self.passwords:
            self.show_message(self.lang_data["error_empty_site"], "Нет паролей")
            return
        
        sites = list(self.passwords.keys())
        dialog = ctk.CTkToplevel(self.window)
        dialog.title(self.lang_data["edit_title"])
        dialog.geometry("350x200")
        dialog.grab_set()
        dialog.transient(self.window)
        
        ctk.CTkLabel(dialog, text=self.lang_data["select_site"]).pack(pady=10)
        combo = ctk.CTkComboBox(dialog, values=sites)
        combo.pack(pady=5)
        
        def confirm():
            site = combo.get()
            if site:
                dialog.destroy()
                self.show_edit_dialog(site)
        
        ctk.CTkButton(dialog, text=self.lang_data["edit"], command=confirm).pack(pady=10)
        ctk.CTkButton(dialog, text=self.lang_data["cancel"], command=dialog.destroy).pack(pady=5)
    
    def show_edit_dialog(self, site):
        data = self.passwords[site]
        dialog = ctk.CTkToplevel(self.window)
        dialog.title(f"{self.lang_data['edit_title']}: {site}")
        dialog.geometry("500x450")
        dialog.grab_set()
        dialog.transient(self.window)
        
        ctk.CTkLabel(dialog, text=self.lang_data["edit_site"]).pack(anchor="w", padx=10, pady=(10,0))
        site_entry = ctk.CTkEntry(dialog, width=450)
        site_entry.insert(0, site)
        site_entry.pack(padx=10, pady=5)
        
        ctk.CTkLabel(dialog, text=self.lang_data["edit_login"]).pack(anchor="w", padx=10)
        username_entry = ctk.CTkEntry(dialog, width=450)
        username_entry.insert(0, data['username'])
        username_entry.pack(padx=10, pady=5)
        
        ctk.CTkLabel(dialog, text=self.lang_data["edit_password"]).pack(anchor="w", padx=10)
        password_entry = ctk.CTkEntry(dialog, width=450)
        password_entry.insert(0, data['password'])
        password_entry.pack(padx=10, pady=5)
        
        def save():
            new_site = site_entry.get().strip()
            new_username = username_entry.get().strip()
            new_password = password_entry.get().strip()
            if not new_site or not new_password:
                return
            
            if new_password != data['password']:
                self.check_and_warn_weak_password(new_password)
            
            del self.passwords[site]
            self.passwords[new_site] = {
                "username": new_username,
                "password": new_password,
                "date_added": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            save_passwords(self.passwords)
            self.refresh_list()
            dialog.destroy()
            self.show_message(self.lang_data["success"], self.lang_data["updated_msg"])
        
        ctk.CTkButton(dialog, text=self.lang_data["save"], command=save).pack(pady=15)
        ctk.CTkButton(dialog, text=self.lang_data["cancel"], command=dialog.destroy).pack(pady=5)
    
    def delete_password(self):
        if not self.passwords:
            self.show_message(self.lang_data["error_empty_site"], "Нет паролей")
            return
        
        select_dialog = ctk.CTkToplevel(self.window)
        select_dialog.title(self.lang_data["delete"])
        select_dialog.geometry("350x250")
        select_dialog.grab_set()
        select_dialog.transient(self.window)
        
        ctk.CTkLabel(select_dialog, text=self.lang_data["select_delete"]).pack(pady=10)
        sites = list(self.passwords.keys())
        combo = ctk.CTkComboBox(select_dialog, values=sites)
        combo.pack(pady=5)
        
        def open_confirm():
            site = combo.get()
            if not site:
                return
            select_dialog.destroy()
            
            confirm_dialog = ctk.CTkToplevel(self.window)
            confirm_dialog.title(self.lang_data["confirm_delete"])
            confirm_dialog.geometry("350x140")
            confirm_dialog.grab_set()
            confirm_dialog.transient(self.window)
            
            ctk.CTkLabel(confirm_dialog, text=self.lang_data["confirm_delete_msg"].format(site)).pack(pady=15)
            
            btn_frame = ctk.CTkFrame(confirm_dialog, fg_color="transparent")
            btn_frame.pack(pady=5)
            
            def do_delete():
                del self.passwords[site]
                save_passwords(self.passwords)
                self.refresh_list()
                confirm_dialog.destroy()
                self.show_message(self.lang_data["success"], self.lang_data["deleted_msg"].format(site))
            
            ctk.CTkButton(btn_frame, text="✅ Да", command=do_delete, width=80).pack(side="left", padx=15)
            ctk.CTkButton(btn_frame, text="❌ Нет", command=confirm_dialog.destroy, width=80).pack(side="left", padx=15)
        
        ctk.CTkButton(select_dialog, text=self.lang_data["delete"], command=open_confirm).pack(pady=10)
        ctk.CTkButton(select_dialog, text=self.lang_data["cancel"], command=select_dialog.destroy).pack(pady=5)
    
    def open_settings(self):
        if self.settings_window and self.settings_window.winfo_exists():
            self.settings_window.lift()
            return
        
        self.settings_window = ctk.CTkToplevel(self.window)
        self.settings_window.title(self.lang_data["settings"])
        self.settings_window.geometry("500x450")
        self.settings_window.grab_set()
        self.settings_window.transient(self.window)
        
        ctk.CTkLabel(self.settings_window, text=self.lang_data["master_password"], font=("Segoe UI", 16, "bold")).pack(pady=15)
        
        master_enabled = is_master_set()
        self.master_switch_var = ctk.BooleanVar(value=master_enabled)
        
        def on_master_toggle():
            if self.master_switch_var.get():
                self.show_set_master_dialog()
            else:
                if master_enabled:
                    confirm = ctk.CTkToplevel(self.settings_window)
                    confirm.title(self.lang_data["confirm_delete"])
                    confirm.geometry("300x140")
                    confirm.grab_set()
                    confirm.transient(self.settings_window)
                    confirm.focus_force()
                    
                    ctk.CTkLabel(confirm, text="Отключить мастер-пароль?").pack(pady=15)
                    
                    btn_frame = ctk.CTkFrame(confirm, fg_color="transparent")
                    btn_frame.pack(pady=5)
                    
                    def do_disable():
                        remove_master_password()
                        confirm.destroy()
                        self.show_message(self.lang_data["success"], self.lang_data["master_removed"])
                        self.master_switch_var.set(False)
                        self.master_switch.configure(text=self.lang_data["master_disabled"])
                    
                    ctk.CTkButton(btn_frame, text="Да", command=do_disable, width=80).pack(side="left", padx=15)
                    ctk.CTkButton(btn_frame, text="Нет", command=confirm.destroy, width=80).pack(side="left", padx=15)
        
        self.master_switch = ctk.CTkSwitch(
            self.settings_window, 
            text=self.lang_data["master_enabled"] if master_enabled else self.lang_data["master_disabled"],
            variable=self.master_switch_var,
            command=on_master_toggle
        )
        self.master_switch.pack(pady=10)
        
        self.change_master_btn = ctk.CTkButton(
            self.settings_window,
            text=self.lang_data["master_change"],
            command=self.show_change_master_dialog,
            width=200
        )
        self.change_master_btn.pack(pady=10)
        
        ctk.CTkFrame(self.settings_window, height=1, fg_color="gray").pack(fill="x", pady=15)
        
        ctk.CTkLabel(self.settings_window, text=self.lang_data["theme"], font=("Segoe UI", 14, "bold")).pack(pady=(10,5))
        
        theme_frame = ctk.CTkFrame(self.settings_window, fg_color="transparent")
        theme_frame.pack(pady=5)
        
        def set_theme(theme):
            self.current_theme = theme
            self.apply_theme()
        
        theme_light_btn = ctk.CTkButton(theme_frame, text=self.lang_data["theme_light"], command=lambda: set_theme("light"), width=120)
        theme_light_btn.pack(side="left", padx=10)
        
        theme_dark_btn = ctk.CTkButton(theme_frame, text=self.lang_data["theme_dark"], command=lambda: set_theme("dark"), width=120)
        theme_dark_btn.pack(side="left", padx=10)
        
        theme_system_btn = ctk.CTkButton(theme_frame, text=self.lang_data["theme_system"], command=lambda: set_theme("system"), width=120)
        theme_system_btn.pack(side="left", padx=10)
        
        ctk.CTkButton(self.settings_window, text=self.lang_data["ok"], command=self.settings_window.destroy, width=100).pack(pady=20)
    
    def show_set_master_dialog(self):
        dialog = ctk.CTkToplevel(self.settings_window)
        dialog.title(self.lang_data["master_first"])
        dialog.geometry("400x250")
        dialog.grab_set()
        
        ctk.CTkLabel(dialog, text=self.lang_data["master_first"]).pack(pady=15)
        pass_entry = ctk.CTkEntry(dialog, show="•", width=250)
        pass_entry.pack(pady=5)
        ctk.CTkLabel(dialog, text=self.lang_data["master_confirm"]).pack()
        confirm_entry = ctk.CTkEntry(dialog, show="•", width=250)
        confirm_entry.pack(pady=5)
        
        def set_it():
            p1 = pass_entry.get()
            p2 = confirm_entry.get()
            if not p1:
                return
            if p1 != p2:
                self.show_error_dialog(self.lang_data["master_mismatch"])
                return
            set_master_password(p1)
            self.master_switch.configure(text=self.lang_data["master_enabled"])
            dialog.destroy()
            self.show_message(self.lang_data["success"], self.lang_data["master_success"])
        
        ctk.CTkButton(dialog, text=self.lang_data["ok"], command=set_it).pack(pady=15)
        ctk.CTkButton(dialog, text=self.lang_data["cancel"], command=dialog.destroy).pack()
    
    def show_change_master_dialog(self):
        if not is_master_set():
            self.show_set_master_dialog()
            return
        
        dialog = ctk.CTkToplevel(self.settings_window)
        dialog.title(self.lang_data["master_change"])
        dialog.geometry("400x300")
        dialog.grab_set()
        
        ctk.CTkLabel(dialog, text=self.lang_data["master_title"]).pack(pady=10)
        old_entry = ctk.CTkEntry(dialog, show="•", width=250)
        old_entry.pack(pady=5)
        
        ctk.CTkLabel(dialog, text=self.lang_data["master_first"]).pack(pady=5)
        new_entry = ctk.CTkEntry(dialog, show="•", width=250)
        new_entry.pack(pady=5)
        
        ctk.CTkLabel(dialog, text=self.lang_data["master_confirm"]).pack()
        confirm_entry = ctk.CTkEntry(dialog, show="•", width=250)
        confirm_entry.pack(pady=5)
        
        def change_it():
            old = old_entry.get()
            if not verify_master(old):
                self.show_error_dialog(self.lang_data["master_wrong"])
                return
            p1 = new_entry.get()
            p2 = confirm_entry.get()
            if p1 != p2:
                self.show_error_dialog(self.lang_data["master_mismatch"])
                return
            if not p1:
                return
            set_master_password(p1)
            dialog.destroy()
            self.show_message(self.lang_data["success"], self.lang_data["master_changed"])
        
        ctk.CTkButton(dialog, text=self.lang_data["save"], command=change_it).pack(pady=15)
        ctk.CTkButton(dialog, text=self.lang_data["cancel"], command=dialog.destroy).pack()
    
    def show_error_dialog(self, message):
        dialog = ctk.CTkToplevel(self.window)
        dialog.title("")
        dialog.geometry("300x100")
        dialog.grab_set()
        dialog.transient(self.window)
        ctk.CTkLabel(dialog, text=message).pack(pady=20)
        ctk.CTkButton(dialog, text=self.lang_data["ok"], command=dialog.destroy).pack()
    
    def export_passwords(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile="passwords_backup.json"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.passwords, f, ensure_ascii=False, indent=4)
                self.show_message(self.lang_data["export_success"], f"{self.lang_data['export_msg']}\n{file_path}")
            except Exception as e:
                self.show_message(self.lang_data["import_error"], str(e))
    
    def import_passwords(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    imported = json.load(f)
                self.passwords.update(imported)
                save_passwords(self.passwords)
                self.refresh_list()
                self.show_message(self.lang_data["import_success"], self.lang_data["import_msg"])
            except Exception as e:
                self.show_message(self.lang_data["import_error"], self.lang_data["import_error_msg"])
    
    def change_language(self):
        langs = list(LANGUAGES.keys())
        dialog = ctk.CTkToplevel(self.window)
        dialog.title(self.lang_data["language"])
        dialog.geometry("280x180")
        dialog.grab_set()
        dialog.transient(self.window)
        
        ctk.CTkLabel(dialog, text="Выберите язык / Select language:").pack(pady=10)
        combo = ctk.CTkComboBox(dialog, values=langs)
        combo.pack(pady=5)
        
        def set_lang():
            selected = combo.get()
            if selected in LANGUAGES:
                self.current_lang = selected
                self.lang_data = LANGUAGES[selected]
                self.update_ui_texts()
                self.refresh_list()
                dialog.destroy()
        
        ctk.CTkButton(dialog, text=self.lang_data["ok"], command=set_lang).pack(pady=10)
        ctk.CTkButton(dialog, text=self.lang_data["cancel"], command=dialog.destroy).pack(pady=5)
    
    def show_message(self, title, message):
        dialog = ctk.CTkToplevel(self.window)
        dialog.title(title)
        dialog.geometry("450x150")
        dialog.grab_set()
        dialog.transient(self.window)
        
        ctk.CTkLabel(dialog, text=message, wraplength=400).pack(pady=20)
        ctk.CTkButton(dialog, text=self.lang_data["ok"], command=dialog.destroy).pack(pady=5)
    
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = PasswordManager()
    app.run()