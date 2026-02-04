# Deployment Guide: TIB-SaaS (Git Workflow)

## Prerequisites
- **VPS**: Hostinger (Ubuntu 20.04/22.04).
- **Domain**: `tib-usa.app` → VPS IP.
- **Git**: Installed on VPS (`apt install git`).
- **Docker**: Installed on VPS.

## 1. Setup Remote (On Your Machine)
If you haven't already linked your Github/Gitlab:
```bash
git remote add origin https://github.com/YOUR_USER/tib-saas.git
git add .
git commit -m "Deployment Ready"
git push -u origin master
```

## 2. Prepare Server (VPS)
SSH into your server:
```bash
ssh root@your_vps_ip
```

Clone the repository:
```bash
cd /var/www
git clone https://github.com/YOUR_USER/tib-saas.git
cd tib-saas
```

## 3. Configuration
Create the production environment file:
```bash
cp .env.example .env
nano .env
```
*Paste your production keys here (Secret Key, Stripe Live Keys).*

## 4. Deploy
Build and start the containers:
```bash
docker-compose up -d --build
```

**HTTPS is Automatic:** Traefik will request a certificate for `tib-usa.app`.

## 5. Updates (Future)
To update the app later, just run inside the folder:
```bash
git pull origin master
docker-compose up -d --build
```
