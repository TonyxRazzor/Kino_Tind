# Kino_Tind

### Подготовка сервера

**Обновляем пакеты:**
```bash
sudo apt update && sudo apt upgrade -y
```

**Устанавливаем необходимые зависимости:**
```bash
sudo apt install -y python3 python3-venv python3-pip git nginx certbot python3-certbot-nginx
```
---
### Виртуальное окружение и зависимости

**Создаём venv:**
```bash
python3 -m venv venv
```

**Активируем окружение:**
```bash
source venv/bin/activate
```

**Устанавливаем зависимости:**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```
============================================================================================
*В ручную:*
```bash
pip install django django-colorfield django-filter psycopg2-binary djoser django-phone-field
```
---
### Настройка Django

**В settings.py:**

*ALLOWED_HOSTS*
```bash
DEBUG = False
ALLOWED_HOSTS = ['kino-tind.ru', 'www.kino-tind.ru', '127.0.0.1']
```

*Статика и медиа*
```bash
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

**Применить миграции:**
```bash
python manage.py migrate
```

**Собрать статику:**
```bash
python manage.py collectstatic
```

**Дать права на чтение**
```bash
sudo chown -R tony:www-data /home/tony/Kino_Tind/staticfiles
sudo chmod -R 755 /home/tony/Kino_Tind/staticfiles
```

**Открыть доступ к домашней директории**
```bash
chmod o+x /home/tony
```

**Суперпользователь**
```bash
python manage.py createsuperuser
```
---
### Настройка Gunicorn (приложение Django)

**Установить gunicorn:**
```bash
pip install gunicorn
```

**Создать systemd unit-файл:**
```bash
sudo nano /etc/systemd/system/kino_tind.service
```

*Вставить:*
```ini
[Unit]
Description=Gunicorn instance to serve Kino_Tind
After=network.target

[Service]
User=tony
Group=www-data
WorkingDirectory=/home/tony/Kino_Tind
Environment="PATH=/home/tony/Kino_Tind/venv/bin"
ExecStart=/home/tony/Kino_Tind/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 Kino_Viewer.wsgi:application

[Install]
WantedBy=multi-user.target
```

**Перезапустить сервис:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable kino_tind
sudo systemctl start kino_tind
sudo systemctl status kino_tind
```
---
### Настройка Nginx

**Создать конфиг:**
```bash
sudo nano /etc/nginx/sites-available/kino_tind
```

**Вставить:**
```nginx
server {
    server_name kino-tind.ru www.kino-tind.ru;

    location /static/ {
        alias /home/tony/Kino_Tind/staticfiles/;
    }

    location /media/ {
        alias /home/tony/Kino_Tind/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    listen 443 ssl;
    ssl_certificate /etc/letsencrypt/live/kino-tind.ru/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/kino-tind.ru/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
}

server {
    listen 80;
    server_name kino-tind.ru www.kino-tind.ru;
    return 301 https://$host$request_uri;
}
```

**Активировать конфиг:**
```bash
sudo ln -s /etc/nginx/sites-available/kino_tind /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl status nginx
```
---
### Настройка SSL (Let's Encrypt)

**Выпустить сертификат:**
```bash
sudo certbot --nginx -d kino-tind.ru -d www.kino-tind.ru
```

Проверить автообновление:
```bash
sudo certbot renew --dry-run
```
---
### Логи и отладка

Логи Django через gunicorn:
```bash
journalctl -u kino_tind -f
```

Логи Nginx:
```bash
tail -f /var/log/nginx/error.log
tail -f /var/log/nginx/access.log
```
