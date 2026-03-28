from flask import Flask, render_template, request # Flask kitabxanasını və lazımi funksiyaları çağırırıq
import sqlite3 # Verilənlər bazası ilə işləmək üçün SQLite3 kitabxanasını çağırırıq
from flask_limiter import Limiter # Giriş sayını məhdudlaşdırmaq üçün Limiter-i çağırırıq
from flask_limiter.util import get_remote_address # İstifadəçinin IP ünvanını tapmaq üçün köməkçi funksiya

app = Flask(__name__) # Flask proqramını başladırıq

# Sayta hücumların (Brute Force) qarşısını almaq üçün limit tənzimləmələri
limiter = Limiter(
    get_remote_address, # Limiti IP ünvanına görə tətbiq et
    app=app, # Bu tənzimləməni bizim proqrama (app) bağla
    default_limits=["100 per day"], # Gün ərzində maksimum 100 sorğu icazəsi ver
    storage_uri="memory://", # Limit məlumatlarını müvəqqəti yaddaşda (RAM) saxla
)

# İstifadəçinin bazada olub-olmadığını yoxlayan funksiya
def check_user_in_db(username, password):
    conn = sqlite3.connect('database.db') # Verilənlər bazasına qoşuluruq
    cursor = conn.cursor() # Baza üzərində əməliyyat aparmaq üçün "kursor" yaradırıq
    # SQL Injection-dan qorunmaq üçün "?" istifadə edərək təhlükəsiz sorğu yazırıq
    query = "SELECT * FROM users WHERE username = ? AND password = ?"
    cursor.execute(query, (username, password)) # Sorğunu icra edirik
    user = cursor.fetchone() # Tapılan istifadəçini götürürük (yoxdursa None qaytarır)
    conn.close() # Bazanı bağlayırıq
    return user # İstifadəçini geri qaytarırıq

# YENİ: Uğursuz giriş cəhdini "failed_logins" cədvəlinə yazan funksiya
def log_failed_attempt(username, ip):
    conn = sqlite3.connect('database.db') # Bazaya qoşuluruq
    cursor = conn.cursor()
    # Səhv daxil edilən adı, IP-ni və vaxtı (vaxt avtomatik yazılır) cədvələ əlavə edirik
    cursor.execute("INSERT INTO failed_logins (username, ip_address) VALUES (?, ?)", (username, ip))
    conn.commit() # Dəyişikliyi bazada yadda saxlayırıq (bu mütləqdir!)
    conn.close() # Bazanı bağlayırıq

# Əsas (Login) səhifəsinin marşrutu
@app.route('/', methods=['GET', 'POST'])
@limiter.limit("5 per minute") # Giriş cəhdini dəqiqədə maksimum 5 dəfə ilə məhdudlaşdırırıq
def login():
    error = None # Başlanğıcda heç bir xəta yoxdur
    if request.method == 'POST': # Əgər istifadəçi formanı doldurub "Login" düyməsini basıbsa
        u_name = request.form['username'] # Formadan istifadəçi adını götürürük
        p_word = request.form['password'] # Formadan şifrəni götürürük
        ip_addr = request.remote_addr # Giriş edən şəxsin IP ünvanını müəyyən edirik

        # Bazada bu istifadəçi və şifrə uyğunluğunu yoxlayırıq
        if check_user_in_db(u_name, p_word):
            # Əgər məlumatlar doğrudursa, göstəriləcək kitablar siyahısı
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
            # Məlumatlar doğrudur, kitablar səhifəsini açırıq
            return render_template('kitablar.html', books=kitablar)
        else:
            # Əgər məlumatlar SƏHVDİRSƏ:
            error = "Invalid username or password!" # Ekranda görünəcək xəta mesajı
            log_failed_attempt(u_name, ip_addr) # Səhv cəhdi bazaya qeyd edirik
            # VS Code terminalında (konsolda) izləmək üçün məlumat yazırıq
            print(f"DIQQƏT: {u_name} üçün uğursuz giriş cəhdi! IP: {ip_addr}") 
    
    # Səhifəni (və ya xəta mesajını) ekranda göstəririk
    return render_template('login.html', error=error)

# Əgər kimsə limiti keçərsə (məsələn 1 dəqiqədə 6-cı dəfə yoxlayarsa) bu xəta görünür
@app.errorhandler(429)
def ratelimit_handler(e):
    return "Too many attempts! Please wait a minute.", 429

# Proqramı işə salırıq
if __name__ == '__main__':
    app.run(debug=True) # Debug rejimi səhvləri görmək üçün aktivdir