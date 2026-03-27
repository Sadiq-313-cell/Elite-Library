from flask import Flask, render_template, request
import sqlite3
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

# Brute Force-un qarşısını almaq üçün limitləyici tənzimləmələri
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["100 per day"], # Ümumi sayt limiti
    storage_uri="memory://",
)

def check_user_in_db(username, password):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    # SQL Injection-dan qorunmaq üçün mütləq "?" istifadə edirik
    query = "SELECT * FROM users WHERE username = ? AND password = ?"
    cursor.execute(query, (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

@app.route('/', methods=['GET', 'POST'])
@limiter.limit("5 per minute") # Giriş cəhdini dəqiqədə 5 ilə məhdudlaşdırırıq
def login():
    error = None
    if request.method == 'POST':
        # Formadan gələn məlumatlar
        u_name = request.form['username']
        p_word = request.form['password']

        # Bazada yoxlayırıq
        if check_user_in_db(u_name, p_word):
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
            error = "Invalid username or password!"
            
    return render_template('login.html', error=error)

# Hər hansı səhifə tapılmadıqda və ya limit keçildikdə xəta mesajı üçün
@app.errorhandler(429)
def ratelimit_handler(e):
    return "Too many attempts! Please wait a minute.", 429

if __name__ == '__main__':
    app.run(debug=True)