from flask import Flask, render_template, request # Veb server və səhifə yönləndirmə funksiyaları
import sqlite3 # Verilənlər bazası (DB) ilə əlaqə üçün
from flask_limiter import Limiter # Giriş cəhdlərini məhdudlaşdıran kitabxana
from flask_limiter.util import get_remote_address # İstifadəçinin IP-sini müəyyən etmək üçün
from werkzeug.security import generate_password_hash, check_password_hash # Parolları təhlükəsiz şifrələmək üçün

app = Flask(__name__) # Flask tətbiqini yaradırıq

# --- TƏHLÜKƏSİZLİK: RATE LIMITER QURAŞDIRILMASI ---
# Bu hissə robotların və ya skriptlərin saniyədə minlərlə sorğu göndərməsinin qarşısını alır.
limiter = Limiter(
    get_remote_address, # Hər bir IP ünvanı üçün ayrı-ayrı limit tətbiq edir
    app=app, 
    default_limits=["100 per day"], # Ümumi olaraq gündəlik 100 sorğu limiti
    storage_uri="memory://", # Limit məlumatlarını müvəqqəti RAM yaddaşda saxlayır
)

# --- FUNKSİYA: İSTİFADƏÇİ YOXLANILMASI (LOGIN) ---
def check_user_in_db(username, password):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    # SQL Injection-dan qorunmaq üçün "?" işarəsindən (parameterized query) istifadə edirik
    query = "SELECT password FROM users WHERE username = ?"
    cursor.execute(query, (username,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        hashed_password = result[0] # Bazadakı şifrələnmiş parolu götürürük
        # Daxil edilən parolu bazadakı heş (hash) ilə təhlükəsiz müqayisə edirik
        if check_password_hash(hashed_password, password):
            return True
    return False

# --- FUNKSİYA: YENİ İSTİFADƏÇİ ƏLAVƏ EDİLMƏSİ (SIGNUP) ---
def add_user_to_db(username, password):
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # Parolu heç vaxt açıq mətndə saxlamırıq! Onu heşləyirik.
        hashed_password = generate_password_hash(password)
        
        # Eyni adda istifadəçinin olub-olmadığını yoxlayırıq
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            conn.close()
            return False, "Username already exists!"
        
        # Bazaya şifrələnmiş (hashed) parolu daxil edirik
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        conn.close()
        return True, "Registration successful! Please login."
    except:
        return False, "Database error!"

# --- FUNKSİYA: UĞURSUZ CƏHDLƏRİN QEYDİYYATI (LOGGING) ---
# Təhlükəsizlik analizi üçün kimin səhv girdiyini bazaya yazırıq
def log_failed_attempt(username, ip):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO failed_logins (username, ip_address) VALUES (?, ?)", (username, ip))
    conn.commit()
    conn.close()

# --- MARŞRUT: LOGİN VƏ QEYDİYYAT SƏHİFƏSİ ---
@app.route('/', methods=['GET', 'POST'])
@limiter.limit("5 per minute") # Brute-force əleyhinə: dəqiqədə maksimum 5 cəhd icazəsi
def login():
    error = "" 
    if request.method == 'POST':
        action = request.form.get('action') # Login yoxsa Signup düyməsinin basıldığını yoxlayırıq
        u_name = request.form['username']
        p_word = request.form['password']
        ip_addr = request.remote_addr # İstifadəçinin IP ünvanını götürürük

        # Əgər Login düyməsi basılıbsa:
        if action == 'login':
            if check_user_in_db(u_name, p_word):
                # Kitablar məlumatı (Uğurlu giriş halında görünəcək siyahı)
                kitablar = [
                    ("Les Misérables", "Victor Hugo", "https://covers.openlibrary.org/b/id/12836262-L.jpg"),
                    ("1984", "George Orwell", "https://covers.openlibrary.org/b/id/12717013-L.jpg"),
                    ("Harry Potter", "J.K. Rowling", "https://covers.openlibrary.org/b/id/10521270-L.jpg"),
                    ("Crime and Punishment", "Fyodor Dostoevsky", "https://covers.openlibrary.org/b/id/12642434-L.jpg"),
                    ("The Alchemist", "Paulo Coelho", "https://covers.openlibrary.org/b/id/12913160-L.jpg"),
                    ("The Great Gatsby", "F. Scott Fitzgerald", "https://covers.openlibrary.org/b/id/12727827-L.jpg"),
                    ("The Little Prince", "Antoine de Saint-Exupéry", "https://covers.openlibrary.org/b/id/12574043-L.jpg"),
                    ("The Picture of Dorian Gray", "Oscar Wilde", "https://covers.openlibrary.org/b/id/12715053-L.jpg"),
                    ("Faust", "Johann Wolfgang von Goethe", "https://covers.openlibrary.org/b/id/12720230-L.jpg"),
                    ("Animal Farm", "George Orwell", "https://covers.openlibrary.org/b/id/12534575-L.jpg"),
                    ("The Hobbit", "J.R.R. Tolkien", "https://covers.openlibrary.org/b/id/12623310-L.jpg"),
                ]
                return render_template('kitablar.html', books=kitablar)
            else:
                # Giriş uğursuzdursa, error göstər və hadisəni log-la
                error = "Invalid username or password!"
                log_failed_attempt(u_name, ip_addr)
                print(f"DIQQƏT: {u_name} üçün uğursuz giriş cəhdi! IP: {ip_addr}") 
        
        # Əgər Signup (Qeydiyyat) düyməsi basılıbsa:
        elif action == 'signup':
            success, message = add_user_to_db(u_name, p_word)
            error = message

    return render_template('login.html', error=error)

# --- XƏTA İDARƏETMƏSİ: LİMİT AŞILDIQDA ---
@app.errorhandler(429)
def ratelimit_handler(e):
    return "Too many attempts! Please wait a minute.", 429

# --- TƏTBİQİ BAŞLADIRIQ ---
if __name__ == '__main__':
    app.run(debug=True)