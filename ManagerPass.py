import os
import json
import customtkinter as ctk
import locale
import random
import string
import hashlib
import time
import csv
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
        "note": "Заметки:",
        "generate": "🎲 Сгенерировать",
        "add": "➕ Добавить",
        "delete": "🗑️ Удалить",
        "saved_passwords": "Сохранённые пароли",
        "search": "Поиск:",
        "clear_search": "Сбросить",
        "empty": "Нет сохранённых паролей",
        "site_header": "Сайт / Сервис",
        "login_header": "Логин",
        "password_header": "Пароль",
        "note_header": "Заметки",
        "copy_login": "📋 Логин",
        "copy_password": "📋 Пароль",
        "copy_note": "📋 Заметки",
        "error_empty_site": "Ошибка",
        "error_empty_site_msg": "Введите название сайта",
        "error_empty_password": "Ошибка",
        "error_empty_password_msg": "Введите пароль",
        "weak_password_warning": "⚠️ Слабый пароль",
        "weak_password_msg": "Пароль слишком простой. Рекомендуется использовать более сложный пароль.",
        "success": "Успех",
        "saved_msg": "Пароль для {} сохранён!",
        "select_delete": "Выберите сайт для удаления:",
        "confirm_delete": "Подтверждение",
        "confirm_delete_msg": "Удалить пароль для {}?",
        "deleted_msg": "Пароль для {} удалён!",
        "copied": "Скопировано",
        "copied_login_msg": "Логин для {} скопирован",
        "copied_pass_msg": "Пароль для {} скопирован",
        "copied_note_msg": "Заметка для {} скопирована",
        "language": "🌐 Язык",
        "by_minux": "By Minux",
        "show_password": "Показать пароль",
        "cancel": "Отмена",
        "ok": "OK",
        "export": "📤 Экспорт JSON",
        "import": "📥 Импорт JSON",
        "export_success": "Экспорт выполнен!",
        "export_msg": "Пароли сохранены в файл:",
        "import_success": "Импорт выполнен!",
        "import_msg": "Пароли восстановлены из файла",
        "import_error": "Ошибка импорта",
        "import_error_msg": "Не удалось импортировать файл",
        "theme": "Тема",
        "theme_light": "Светлая",
        "theme_dark": "Тёмная",
        "theme_system": "Системная",
        "search_count": "Найдено: {}",
        "csv_export": "📊 Экспорт CSV",
        "csv_success": "Экспорт в CSV выполнен!"
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
        "note": "Notes:",
        "generate": "🎲 Generate",
        "add": "➕ Add",
        "delete": "🗑️ Delete",
        "saved_passwords": "Saved Passwords",
        "search": "Search:",
        "clear_search": "Clear",
        "empty": "No saved passwords",
        "site_header": "Site / Service",
        "login_header": "Login",
        "password_header": "Password",
        "note_header": "Notes",
        "copy_login": "📋 Login",
        "copy_password": "📋 Password",
        "copy_note": "📋 Note",
        "error_empty_site": "Error",
        "error_empty_site_msg": "Enter site name",
        "error_empty_password": "Error",
        "error_empty_password_msg": "Enter password",
        "weak_password_warning": "⚠️ Weak Password",
        "weak_password_msg": "This password is too simple. Use a stronger password.",
        "success": "Success",
        "saved_msg": "Password for {} saved!",
        "select_delete": "Select site to delete:",
        "confirm_delete": "Confirm",
        "confirm_delete_msg": "Delete password for {}?",
        "deleted_msg": "Password for {} deleted!",
        "copied": "Copied",
        "copied_login_msg": "Login for {} copied",
        "copied_pass_msg": "Password for {} copied",
        "copied_note_msg": "Note for {} copied",
        "language": "🌐 Language",
        "by_minux": "By Minux",
        "show_password": "Show password",
        "cancel": "Cancel",
        "ok": "OK",
        "export": "📤 Export JSON",
        "import": "📥 Import JSON",
        "export_success": "Export completed!",
        "export_msg": "Passwords saved to file:",
        "import_success": "Import completed!",
        "import_msg": "Passwords restored from file",
        "import_error": "Import error",
        "import_error_msg": "Failed to import file",
        "theme": "Theme",
        "theme_light": "Light",
        "theme_dark": "Dark",
        "theme_system": "System",
        "search_count": "Found: {}",
        "csv_export": "📊 Export CSV",
        "csv_success": "CSV export completed!"
    },
    "Türkçe": {
        "title": "Şifre Yöneticisi",
        "settings": "⚙️ Ayarlar",
        "master_password": "Ana Şifre",
        "master_enabled": "Ana şifreyi etkinleştir",
        "master_disabled": "Ana şifreyi devre dışı bırak",
        "master_change": "Ana şifreyi değiştir",
        "master_forgot": "Ana şifrenizi mi unuttunuz?",
        "master_forgot_help": "Anahtar dosyası oluşturuldu. Programı yeniden başlatın.",
        "master_title": "Ana şifreyi girin",
        "master_first": "Ana şifre oluşturun",
        "master_confirm": "Şifreyi onaylayın",
        "master_mismatch": "Şifreler eşleşmiyor",
        "master_wrong": "Yanlış ana şifre",
        "master_success": "Ana şifre ayarlandı!",
        "master_removed": "Ana şifre devre dışı bırakıldı!",
        "master_changed": "Ana şifre değiştirildi!",
        "master_blocked": "Çok fazla deneme. {} saniye bekleyin.",
        "site": "Site / Hizmet:",
        "login": "Kullanıcı Adı:",
        "password": "Şifre:",
        "note": "Notlar:",
        "generate": "🎲 Oluştur",
        "add": "➕ Ekle",
        "delete": "🗑️ Sil",
        "saved_passwords": "Kaydedilen Şifreler",
        "search": "Ara:",
        "clear_search": "Temizle",
        "empty": "Kayıtlı şifre yok",
        "site_header": "Site / Hizmet",
        "login_header": "Kullanıcı Adı",
        "password_header": "Şifre",
        "note_header": "Notlar",
        "copy_login": "📋 Kullanıcı",
        "copy_password": "📋 Şifre",
        "copy_note": "📋 Not",
        "error_empty_site": "Hata",
        "error_empty_site_msg": "Site adını girin",
        "error_empty_password": "Hata",
        "error_empty_password_msg": "Şifreyi girin",
        "weak_password_warning": "⚠️ Zayıf Şifre",
        "weak_password_msg": "Bu şifre çok basit. Daha güçlü bir şifre kullanın.",
        "success": "Başarılı",
        "saved_msg": "{} için şifre kaydedildi!",
        "select_delete": "Silinecek siteyi seçin:",
        "confirm_delete": "Onay",
        "confirm_delete_msg": "{} için şifre silinsin mi?",
        "deleted_msg": "{} için şifre silindi!",
        "copied": "Kopyalandı",
        "copied_login_msg": "{} için kullanıcı adı kopyalandı",
        "copied_pass_msg": "{} için şifre kopyalandı",
        "copied_note_msg": "{} için not kopyalandı",
        "language": "🌐 Dil",
        "by_minux": "Minux",
        "show_password": "Şifreyi göster",
        "cancel": "İptal",
        "ok": "Tamam",
        "export": "📤 Dışa Aktar JSON",
        "import": "📥 İçe Aktar JSON",
        "export_success": "Dışa aktarma tamamlandı!",
        "export_msg": "Şifreler dosyaya kaydedildi:",
        "import_success": "İçe aktarma tamamlandı!",
        "import_msg": "Şifreler dosyadan geri yüklendi",
        "import_error": "İçe aktarma hatası",
        "import_error_msg": "Dosya içe aktarılamadı",
        "theme": "Tema",
        "theme_light": "Açık",
        "theme_dark": "Koyu",
        "theme_system": "Sistem",
        "search_count": "Bulunan: {}",
        "csv_export": "📊 CSV'ye Aktar",
        "csv_success": "CSV dışa aktarma tamamlandı!"
    },
    "Deutsch": {
        "title": "Passwort-Manager",
        "settings": "⚙️ Einstellungen",
        "master_password": "Master-Passwort",
        "master_enabled": "Master-Passwort aktivieren",
        "master_disabled": "Master-Passwort deaktivieren",
        "master_change": "Master-Passwort ändern",
        "master_forgot": "Master-Passwort vergessen?",
        "master_forgot_help": "Schlüsseldatei erstellt. Starten Sie das Programm neu.",
        "master_title": "Master-Passwort eingeben",
        "master_first": "Master-Passwort erstellen",
        "master_confirm": "Passwort bestätigen",
        "master_mismatch": "Passwörter stimmen nicht überein",
        "master_wrong": "Falsches Master-Passwort",
        "master_success": "Master-Passwort gesetzt!",
        "master_removed": "Master-Passwort deaktiviert!",
        "master_changed": "Master-Passwort geändert!",
        "master_blocked": "Zu viele Versuche. Warten Sie {} Sekunden.",
        "site": "Website / Dienst:",
        "login": "Benutzername:",
        "password": "Passwort:",
        "note": "Notizen:",
        "generate": "🎲 Generieren",
        "add": "➕ Hinzufügen",
        "delete": "🗑️ Löschen",
        "saved_passwords": "Gespeicherte Passwörter",
        "search": "Suchen:",
        "clear_search": "Löschen",
        "empty": "Keine gespeicherten Passwörter",
        "site_header": "Website / Dienst",
        "login_header": "Benutzername",
        "password_header": "Passwort",
        "note_header": "Notizen",
        "copy_login": "📋 Benutzername",
        "copy_password": "📋 Passwort",
        "copy_note": "📋 Notiz",
        "error_empty_site": "Fehler",
        "error_empty_site_msg": "Website-Namen eingeben",
        "error_empty_password": "Fehler",
        "error_empty_password_msg": "Passwort eingeben",
        "weak_password_warning": "⚠️ Schwaches Passwort",
        "weak_password_msg": "Dieses Passwort ist zu einfach. Verwenden Sie ein stärkeres Passwort.",
        "success": "Erfolg",
        "saved_msg": "Passwort für {} gespeichert!",
        "select_delete": "Website zum Löschen auswählen:",
        "confirm_delete": "Bestätigen",
        "confirm_delete_msg": "Passwort für {} löschen?",
        "deleted_msg": "Passwort für {} gelöscht!",
        "copied": "Kopiert",
        "copied_login_msg": "Benutzername für {} kopiert",
        "copied_pass_msg": "Passwort für {} kopiert",
        "copied_note_msg": "Notiz für {} kopiert",
        "language": "🌐 Sprache",
        "by_minux": "Minux",
        "show_password": "Passwort anzeigen",
        "cancel": "Abbrechen",
        "ok": "OK",
        "export": "📤 Exportieren JSON",
        "import": "📥 Importieren JSON",
        "export_success": "Export abgeschlossen!",
        "export_msg": "Passwörter in Datei gespeichert:",
        "import_success": "Import abgeschlossen!",
        "import_msg": "Passwörter aus Datei wiederhergestellt",
        "import_error": "Importfehler",
        "import_error_msg": "Datei konnte nicht importiert werden",
        "theme": "Thema",
        "theme_light": "Hell",
        "theme_dark": "Dunkel",
        "theme_system": "System",
        "search_count": "Gefunden: {}",
        "csv_export": "📊 CSV-Export",
        "csv_success": "CSV-Export abgeschlossen!"
    },
    "中文": {
        "title": "密码管理器",
        "settings": "⚙️ 设置",
        "master_password": "主密码",
        "master_enabled": "启用主密码",
        "master_disabled": "禁用主密码",
        "master_change": "更改主密码",
        "master_forgot": "忘记主密码？",
        "master_forgot_help": "密钥文件已创建。请重启程序。",
        "master_title": "输入主密码",
        "master_first": "创建主密码",
        "master_confirm": "确认密码",
        "master_mismatch": "密码不匹配",
        "master_wrong": "主密码错误",
        "master_success": "主密码已设置！",
        "master_removed": "主密码已禁用！",
        "master_changed": "主密码已更改！",
        "master_blocked": "尝试次数过多。请等待 {} 秒。",
        "site": "网站 / 服务:",
        "login": "用户名:",
        "password": "密码:",
        "note": "备注:",
        "generate": "🎲 生成",
        "add": "➕ 添加",
        "delete": "🗑️ 删除",
        "saved_passwords": "已保存的密码",
        "search": "搜索:",
        "clear_search": "清除",
        "empty": "没有保存的密码",
        "site_header": "网站 / 服务",
        "login_header": "用户名",
        "password_header": "密码",
        "note_header": "备注",
        "copy_login": "📋 用户名",
        "copy_password": "📋 密码",
        "copy_note": "📋 备注",
        "error_empty_site": "错误",
        "error_empty_site_msg": "请输入网站名称",
        "error_empty_password": "错误",
        "error_empty_password_msg": "请输入密码",
        "weak_password_warning": "⚠️ 弱密码",
        "weak_password_msg": "此密码太简单。请使用更强的密码。",
        "success": "成功",
        "saved_msg": "{} 的密码已保存！",
        "select_delete": "选择要删除的网站:",
        "confirm_delete": "确认",
        "confirm_delete_msg": "删除 {} 的密码？",
        "deleted_msg": "{} 的密码已删除！",
        "copied": "已复制",
        "copied_login_msg": "{} 的用户名已复制",
        "copied_pass_msg": "{} 的密码已复制",
        "copied_note_msg": "{} 的备注已复制",
        "language": "🌐 语言",
        "by_minux": "Minux",
        "show_password": "显示密码",
        "cancel": "取消",
        "ok": "确定",
        "export": "📤 导出 JSON",
        "import": "📥 导入 JSON",
        "export_success": "导出完成！",
        "export_msg": "密码已保存到文件：",
        "import_success": "导入完成！",
        "import_msg": "密码已从文件恢复",
        "import_error": "导入错误",
        "import_error_msg": "无法导入文件",
        "theme": "主题",
        "theme_light": "亮色",
        "theme_dark": "暗色",
        "theme_system": "系统",
        "search_count": "找到: {}",
        "csv_export": "📊 导出 CSV",
        "csv_success": "CSV 导出完成！"
    }
}

def get_system_language():
    try:
        lang_code = locale.getdefaultlocale()[0]
        if lang_code:
            if lang_code.startswith('ru'):
                return "Русский"
            elif lang_code.startswith('tr'):
                return "Türkçe"
            elif lang_code.startswith('de'):
                return "Deutsch"
            elif lang_code.startswith('zh'):
                return "中文"
        return "English"
    except:
        return "English"

# ==================== ОСНОВНОЙ КЛАСС ====================
class PasswordManager:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("ManagerPass")
        self.window.geometry("1400x800")
        self.window.minsize(1200, 700)
        
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
        
        self.csv_export_btn = ctk.CTkButton(btn_right_frame, text="", command=self.export_csv, width=100)
        self.csv_export_btn.pack(side="left", padx=5)
        
        self.import_btn = ctk.CTkButton(btn_right_frame, text="", command=self.import_passwords, width=100)
        self.import_btn.pack(side="left", padx=5)
        
        self.lang_button = ctk.CTkButton(btn_right_frame, text="", width=100, command=self.change_language)
        self.lang_button.pack(side="left", padx=5)
        
        form_frame = ctk.CTkFrame(self.main_frame)
        form_frame.pack(fill="x", pady=(0, 15))
        
        self.site_label = ctk.CTkLabel(form_frame, text="")
        self.site_label.grid(row=0, column=0, padx=10, pady=8, sticky="w")
        self.site_entry = ctk.CTkEntry(form_frame, width=280, placeholder_text="google.com")
        self.site_entry.grid(row=0, column=1, padx=10, pady=8)
        
        self.login_label = ctk.CTkLabel(form_frame, text="")
        self.login_label.grid(row=1, column=0, padx=10, pady=8, sticky="w")
        self.username_entry = ctk.CTkEntry(form_frame, width=280, placeholder_text="user@example.com")
        self.username_entry.grid(row=1, column=1, padx=10, pady=8)
        
        self.password_label = ctk.CTkLabel(form_frame, text="")
        self.password_label.grid(row=2, column=0, padx=10, pady=8, sticky="w")
        
        password_row = ctk.CTkFrame(form_frame, fg_color="transparent")
        password_row.grid(row=2, column=1, padx=10, pady=8, sticky="w")
        
        self.password_entry = ctk.CTkEntry(password_row, width=180, placeholder_text="••••••••", show="•")
        self.password_entry.pack(side="left", padx=(0, 8))
        
        self.generate_btn = ctk.CTkButton(password_row, text="", width=70, command=self.generate_password)
        self.generate_btn.pack(side="left", padx=(0, 8))
        
        self.show_pass_check = ctk.CTkCheckBox(password_row, text="", command=self.toggle_password_visibility)
        self.show_pass_check.pack(side="left")
        
        self.note_label = ctk.CTkLabel(form_frame, text="")
        self.note_label.grid(row=3, column=0, padx=10, pady=8, sticky="w")
        self.note_entry = ctk.CTkEntry(form_frame, width=280, placeholder_text="Доп. информация")
        self.note_entry.grid(row=3, column=1, padx=10, pady=8)
        
        btn_frame = ctk.CTkFrame(self.main_frame)
        btn_frame.pack(fill="x", pady=(0, 15))
        
        self.add_btn = ctk.CTkButton(btn_frame, text="", command=self.add_password, width=120)
        self.add_btn.pack(side="left", padx=5)
        
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
        
        self.search_count_label = ctk.CTkLabel(search_frame, text="", width=80)
        self.search_count_label.pack(side="left", padx=5)
        
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
        self.csv_export_btn.configure(text=self.lang_data["csv_export"])
        self.import_btn.configure(text=self.lang_data["import"])
        
        self.site_label.configure(text=self.lang_data["site"])
        self.login_label.configure(text=self.lang_data["login"])
        self.password_label.configure(text=self.lang_data["password"])
        self.note_label.configure(text=self.lang_data["note"])
        self.generate_btn.configure(text=self.lang_data["generate"])
        self.show_pass_check.configure(text=self.lang_data["show_password"])
        
        self.add_btn.configure(text=self.lang_data["add"])
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
            items = [(s, d) for s, d in items if search_text in s.lower() or search_text in d.get('username', '').lower() or search_text in d.get('note', '').lower()]
        
        count = len(items)
        self.search_count_label.configure(text=self.lang_data["search_count"].format(count) if search_text else "")
        
        if not items:
            empty_label = ctk.CTkLabel(self.tree_frame, text=self.lang_data["empty"], text_color="gray")
            empty_label.pack(pady=20)
            return
        
        header = ctk.CTkFrame(self.tree_frame)
        header.pack(fill="x", pady=(0, 5))
        ctk.CTkLabel(header, text=self.lang_data["site_header"], font=("Segoe UI", 12, "bold"), width=280).pack(side="left", padx=5)
        ctk.CTkLabel(header, text=self.lang_data["login_header"], font=("Segoe UI", 12, "bold"), width=220).pack(side="left", padx=5)
        ctk.CTkLabel(header, text=self.lang_data["password_header"], font=("Segoe UI", 12, "bold"), width=180).pack(side="left", padx=5)
        ctk.CTkLabel(header, text=self.lang_data["note_header"], font=("Segoe UI", 12, "bold"), width=200).pack(side="left", padx=5)
        ctk.CTkLabel(header, text="", width=120).pack(side="left")
        
        for site, data in items:
            row = ctk.CTkFrame(self.tree_frame)
            row.pack(fill="x", pady=2)
            
            site_var = ctk.StringVar(value=site)
            site_entry = ctk.CTkEntry(row, textvariable=site_var, width=280)
            site_entry.pack(side="left", padx=5)
            site_entry.bind("<FocusOut>", lambda e, s=site, var=site_var: self.edit_cell(s, "site", var.get()))
            
            login_var = ctk.StringVar(value=data.get('username', ''))
            login_entry = ctk.CTkEntry(row, textvariable=login_var, width=220)
            login_entry.pack(side="left", padx=5)
            login_entry.bind("<FocusOut>", lambda e, s=site, var=login_var: self.edit_cell(s, "login", var.get()))
            
            password_var = ctk.StringVar(value=data.get('password', ''))
            password_entry = ctk.CTkEntry(row, textvariable=password_var, width=180, show="•")
            password_entry.pack(side="left", padx=5)
            password_entry.bind("<FocusOut>", lambda e, s=site, var=password_var: self.edit_cell(s, "password", var.get()))
            
            note_var = ctk.StringVar(value=data.get('note', ''))
            note_entry = ctk.CTkEntry(row, textvariable=note_var, width=200)
            note_entry.pack(side="left", padx=5)
            note_entry.bind("<FocusOut>", lambda e, s=site, var=note_var: self.edit_cell(s, "note", var.get()))
            
            btn_frame = ctk.CTkFrame(row, fg_color="transparent")
            btn_frame.pack(side="left", padx=5)
            
            copy_login_btn = ctk.CTkButton(btn_frame, text=self.lang_data["copy_login"], width=70, command=lambda s=site, u=data.get('username', ''): self.copy_login(s, u))
            copy_login_btn.pack(side="left", padx=2)
            
            copy_pass_btn = ctk.CTkButton(btn_frame, text=self.lang_data["copy_password"], width=70, command=lambda s=site, p=data.get('password', ''): self.copy_password(s, p))
            copy_pass_btn.pack(side="left", padx=2)
            
            copy_note_btn = ctk.CTkButton(btn_frame, text=self.lang_data["copy_note"], width=70, command=lambda s=site, n=data.get('note', ''): self.copy_note(s, n))
            copy_note_btn.pack(side="left", padx=2)
    
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
            elif field == "note":
                self.passwords[site]['note'] = new_value
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
    
    def copy_note(self, site, note):
        self.window.clipboard_clear()
        self.window.clipboard_append(note)
        self.show_message(self.lang_data["copied"], self.lang_data["copied_note_msg"].format(site))
    
    def add_password(self):
        site = self.site_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        note = self.note_entry.get().strip()
        
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
            "note": note,
            "date_added": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        save_passwords(self.passwords)
        
        self.site_entry.delete(0, "end")
        self.username_entry.delete(0, "end")
        self.password_entry.delete(0, "end")
        self.note_entry.delete(0, "end")
        
        self.refresh_list()
        self.show_message(self.lang_data["success"], self.lang_data["saved_msg"].format(site))
    
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
        dialog.geometry("400x380")
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
        
        error_label = ctk.CTkLabel(dialog, text="", text_color="red")
        error_label.pack(pady=5)
        
        def change_it():
            old = old_entry.get()
            if not verify_master(old):
                error_label.configure(text=self.lang_data["master_wrong"])
                return
            p1 = new_entry.get()
            p2 = confirm_entry.get()
            if p1 != p2:
                error_label.configure(text=self.lang_data["master_mismatch"])
                return
            if not p1:
                error_label.configure(text="Введите пароль")
                return
            set_master_password(p1)
            dialog.destroy()
            self.show_message(self.lang_data["success"], self.lang_data["master_changed"])
        
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=15)
        ctk.CTkButton(btn_frame, text=self.lang_data["ok"], command=change_it, width=100).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text=self.lang_data["cancel"], command=dialog.destroy, width=100).pack(side="left", padx=10)
    
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
    
    def export_csv(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile="passwords_export.csv"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8-sig', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(["Site", "Username", "Password", "Note", "Date Added"])
                    for site, data in self.passwords.items():
                        writer.writerow([
                            site,
                            data.get('username', ''),
                            data.get('password', ''),
                            data.get('note', ''),
                            data.get('date_added', '')
                        ])
                self.show_message(self.lang_data["csv_success"], f"{self.lang_data['export_msg']}\n{file_path}")
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
