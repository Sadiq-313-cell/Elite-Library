1.	Giriş
Bu layihə, istifadəçilərin sistemə daxil olaraq kitablar haqqında məlumatları idarə edə biləcəyi dinamik bir veb tətbiqdir. Layihə Visual Studio Code mühitində hazırlanmış, Python (Flask) backend və SQLite verilənlər bazası üzərində qurulmuşdur.Veb səhifə SQL Database ilə əlaqələndirilmişdir.
2.	Texniki Arxivtektura
Layihə "Client-Server" modelinə əsaslanır:
Backend: Server tərəfi Python-un Flask framework-ü ilə idarə olunur.
Frontend: İstifadəçi interfeysi HTML5 və CSS3 (Glassmorphism stili) ilə yığılıb.
Database: Məlumatların saxlanılması üçün SQLite relyasion verilənlər bazasından istifadə edilib.
3.	Verilənlər Bazası Strukturu
Bazada users adlı cədvəl yaradılıb. Cədvəl aşağıdakı sütunlardan ibarətdir:

username (Mətn): İstifadəçi loginini saxlayır.

password (Mətn): İstifadəçi şifrəsini saxlayır.
4.	Təhlükəsizlik Tədbirləri 
Layihədə proqram təminatının təhlükəsizliyini təmin etmək üçün iki əsas mexanizm tətbiq olunub:

Rate Limiting (Sorğu Limiti): Flask-Limiter vasitəsilə eyni IP-dən gələn giriş cəhdləri dəqiqədə 5 ilə məhdudlaşdırılıb (Brute Force hücumlarına qarşı).

SQL Injection Qoruması: Bazaya göndərilən sorğular birbaşa mətn kimi deyil, parametrli (Prepared Statements) şəkildə göndərilir.
5.	Funksionallıq
Login Sistemi: İstifadəçi məlumatları bazadakı qeydlərlə uyğunlaşdıqda sistemə girişə icazə verilir.

Dinamik Siyahı: Giriş uğurlu olduqda, server tərəfindəki kitab siyahısı (ad, müəllif və üz qabığı şəkli) brauzerə ötürülür və vizual olaraq əks etdirilir.

UX Elementləri: JavaScript vasitəsilə şifrənin gizlədilməsi/göstərilməsi və giriş zamanı "Processing..." statusunun göstərilməsi təmin edilib.
      Vacib qeyd:
1.“Flask” veb-serveri qurmaq və səhifələr arası keçidi təmin etmək üçün,”Flask-Limiter” isə login səhifəsini 'Brute Force' hücumlarından qorumaq və təhlükəsizlik limitləri qoymaq üçün istifadə olunub.Layihəni işlədə bilmək üçün terminalda “pip install flask flask-limiter” komandası yazılmalıdır.

2.SQL Database-də məlumatlar binary halda saxlanıldığı üçün məlumatlar oxunaqlı deyil.Database məlumatlarını oxunaqlı şəkildə görmək üçün database-i “open with SQLite3 Editor” etmək lazımdır.

