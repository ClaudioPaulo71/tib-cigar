# The Cigar Room (TIB-SaaS) 🥃

**The Cigar Room** is a premium digital ledger designed for the modern aficionado. It transforms the act of smoking into a data-driven experience, tracking your collection, sensory experiences, and portfolio value with elegance.

## ✨ Features

-   **The Humidor**: Complete inventory management (Quantity, Age, Format).
-   **Sensory Ledger**: Detailed smoking sessions with 3-axis rating sliders (Flavor, Strength, Overall).
-   **Smart Analytics**: Visual dashboard tracking Origin distribution, Brand preferences, and Asset valuation.
-   **Community Library**: Global database of cigars to quickly populate your personal collection.
-   **High-Impact UI**: "Gentlemen's Club" aesthetic with gold accents, leather textures, and dark modes.

## 🛠️ Tech Stack

-   **Backend**: Python 3.10+ (FastAPI), SQLModel (SQLite).
-   **Frontend**: Jinja2, TailwindCSS, Chart.js.
-   **Deployment**: Docker Compose (Port 8002), Nginx Reverse Proxy.

## 🚀 Deployment (Production)

This application is designed to run behind a reverse proxy (Nginx/Apache).

1.  **Clone & Configure**:
    ```bash
    git clone https://github.com/ClaudioPaulo71/tib-cigar.git
    cd tib-cigar
    cp .env.example .env
    ```

2.  **Run with Docker**:
    ```bash
    docker compose up -d --build
    ```
    *App runs on `localhost:8002`.*

3.  **Proxy Setup (Nginx)**:
    Point your Nginx to proxy `http://localhost:8002` and use Certbot for SSL.

## 📦 Local Development

1.  **Install**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

2.  **Run**:
    ```bash
    uvicorn main:app --reload
    ```
    Access at `http://127.0.0.1:8000`.

## 📄 License
Private Property of TIB Technology.
