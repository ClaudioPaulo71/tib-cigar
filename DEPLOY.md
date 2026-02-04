# Deployment Guide: TIB-Cigar (Reverse Proxy)

## Architecture
- **App Port**: `8002` (Internal)
- **Host Server**: Apache/Nginx (Handles SSL & Public Traffic on 443)
- **Persistence**: `./data/tib_saas.db`

## 1. Quick Update (Server)
Since you already have the repo:
```bash
git pull origin master
docker compose down --remove-orphans
docker compose up -d --build
```
*The app is now running on localhost:8002.*

## 2. Configure Host Proxy (Apache/Nginx)
You need to tell your main web server to send traffic from `tib-usa.app` to port `8002`.

### Option A: Using Nginx
Create `/etc/nginx/sites-available/tib-cigar`:
```nginx
server {
    server_name tib-usa.app;

    location / {
        proxy_pass http://localhost:8002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Option B: Using Apache
Create/Edit conf file:
```apache
<VirtualHost *:80>
    ServerName tib-usa.app
    ProxyPreserveHost On
    ProxyPass / http://localhost:8002/
    ProxyPassReverse / http://localhost:8002/
</VirtualHost>
```

## 3. SSL (Certbot)
Run Certbot to secure the domain automatically:
```bash
certbot --nginx -d tib-usa.app
# OR
certbot --apache -d tib-usa.app
```
