# TIB SaaS Ecosystem 🚀

**Target - Identify - Ballistics (TIB)** is a Modular Monolith SaaS designed to manage high-value assets. It currently features two primary modules:
1.  **Garage**: Complete fleet management (Maintenance, Valuation, Mileage).
2.  **Armory (Range)**: Firearm inventory and session logging (Rounds fired, Maintenance).

## ✨ Features

-   **Multi-tenancy**: Complete data isolation per user.
-   **Authentication**: Secure JWT-based login with HttpOnly cookies.
-   **Analytics Dashboard**: Real-time calculation of fleet value, ammo usage, and asset counts.
-   **High-Impact UI**:
    -   *Garage*: Premium Automotive Night Mode ("The Showroom").
    -   *Range*: Tactical HUD interface ("The Armory").

## 🛠️ Tech Stack

-   **Backend**: Python 3.10+, FastAPI, SQLModel (SQLite).
-   **Frontend**: Jinja2 Templates, TailwindCSS, HTMX.
-   **Containerization**: Docker & Docker Compose.

## 🚀 Quick Start (Docker)

The easiest way to run TIB SaaS is with Docker.

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/your-username/tib-saas.git
    cd tib-saas
    ```

2.  **Set up Environment**:
    Copy `.env.example` (or create one) with your secret keys.
    ```bash
    # Create a .env file
    SECRET_KEY=your_secret_key
    ALGORITHM=HS256
    ACCESS_TOKEN_EXPIRE_MINUTES=60
    DATABASE_URL=sqlite:///data/tib_saas.db
    ```

3.  **Run with Docker Compose**:
    ```bash
    docker-compose up -d
    ```

4.  **Access the App**:
    Open `http://localhost:8000`

## 📦 Manual Installation (Dev)

1.  **Create Virtual Env**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Run Server**:
    ```bash
    uvicorn main:app --reload
    ```

## 📄 License
Private Property of TIB Technology.
