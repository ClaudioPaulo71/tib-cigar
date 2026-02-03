# Deployment Guide - TIB SaaS 🚀

This guide explains how to deploy the TIB-SaaS application to your Hostinger VPS using Docker.

## Prerequisites

1.  **Docker & Git installed on VPS**:
    ```bash
    # Run on your VPS
    sudo apt update
    sudo apt install -y git docker.io docker-compose
    ```

## Step 1: Upload Code

Since you have the code on your local machine, you have two options:

### Option A: Via Git (Recommended)
1.  Push your code to a private GitHub/GitLab repo.
2.  Clone it on the server:
    ```bash
    git clone https://github.com/your-username/tib-saas.git
    cd tib-saas
    ```

### Option B: Via SCP (Direct Copy)
If you don't want to use GitHub yet, copy the folder directly:
```bash
# Run this from your LOCAL machine terminal
scp -r /home/crpaulo71/TIB-SaaS root@YOUR_SERVER_IP:/var/www/tib-saas
```

## Step 2: Configure Environment

1.  SSH into your server:
    ```bash
    ssh root@YOUR_SERVER_IP
    cd /var/www/tib-saas
    ```
2.  Create the production `.env` file (NEVER commit this to Git!):
    ```bash
    nano .env
    ```
3.  Paste your production keys (Change SECRET_KEY!):
    ```ini
    SECRET_KEY=CHANGE_THIS_TO_A_VERY_LONG_RANDOM_STRING
    ALGORITHM=HS256
    ACCESS_TOKEN_EXPIRE_MINUTES=60
    DATABASE_URL=sqlite:///data/tib_saas.db
    ```

## Step 3: Launch with Docker

Run the application container:
```bash
sudo docker-compose up -d --build
```

-   **`up -d`**: Runs in background (detached).
-   **`--build`**: Forces a rebuild of the image.

## Step 4: Reverse Proxy (Nginx)

Since you already have a site on Hostinger, you likely use Nginx. To make this app accessible via a domain (e.g., `app.yoursite.com` or `yoursite.com/app`), add this block to your Nginx config:

```nginx
server {
    server_name app.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Check configuration and restart Nginx:
```bash
sudo nginx -t
sudo systemctl restart nginx
```

## Maintenance

-   **View Logs**: `docker-compose logs -f`
-   **Stop App**: `docker-compose down`
-   **Update**:
    1.  `git pull` (or re-upload files)
    2.  `docker-compose up -d --build`
