# AIOne Scraper 🚀

A comprehensive, full-stack web scraping application built with React, Flask, and MongoDB. AIOne Scraper provides a powerful dashboard to extract, view, and manage data from multiple platforms including Reddit, Instagram, YouTube, LinkedIn, OpenTable, Google Maps, and more.

## ✨ Features

- **Multi-Platform Scraping**: Built-in scrapers for various social media and directory platforms.
- **Modern Dashboard**: A sleek, responsive frontend built with React, Vite, and TailwindCSS.
- **Robust Backend**: Flask REST API handling scraping tasks, authentication, and database operations.
- **Database Integration**: MongoDB integration for reliable data storage and retrieval.
- **Authentication System**: Secure user login and role-based access control (RBAC).
- **Docker Support**: Easy deployment and containerization with Docker Compose.

## 🛠️ Technology Stack

- **Frontend**: React 18, Vite, TailwindCSS, Framer Motion, Lucide React
- **Backend**: Python, Flask, PyMongo
- **Database**: MongoDB (Local or Atlas)
- **Deployment**: Docker, Docker Compose, Caddy Server

## 🚀 Getting Started

### Prerequisites

- [Node.js](https://nodejs.org/) (v18+ recommended)
- [Python 3.9+](https://www.python.org/)
- [MongoDB Community Server](https://www.mongodb.com/try/download/community) (or MongoDB Atlas)
- *Optional: [Docker Desktop](https://www.docker.com/products/docker-desktop/) for containerized deployment*

### Option 1: Running Locally (Without Docker)

#### 1. Setup the Database
Ensure your MongoDB service is running locally on `localhost:27017`.

#### 2. Start the Backend
```bash
cd backend
python -m venv venv
# Activate the virtual environment
# Windows:
.\venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
python app.py
```
*The backend will run on `http://127.0.0.1:61631`.*

#### 3. Start the Frontend
Open a new terminal window:
```bash
cd frontend
npm install
npm run dev
```
*The frontend will be available at `http://localhost:5173`.*

### Option 2: Running with Docker

If you have Docker Desktop installed, you can start the entire stack (Frontend, Backend, Database, and Caddy Web Server) with a single command:

```bash
docker-compose up -d --build
```
*(If using the newer Docker CLI, use `docker compose up -d --build`)*

## 📂 Project Structure

```text
AIOne_Scrapper-main/
├── backend/               # Flask API and Python Scraping Scripts
│   ├── app.py             # Main Flask application entry point
│   ├── db.py              # MongoDB connection configuration
│   ├── requirements.txt   # Python dependencies
│   └── *_scraper.py       # Various platform-specific scraper logic
├── frontend/              # React/Vite application
│   ├── src/               # React components, pages, and styles
│   ├── package.json       # Node.js dependencies and scripts
│   └── vite.config.ts     # Vite configuration
├── docker-compose.yml     # Docker composition for multi-container deployment
└── Caddyfile              # Caddy web server configuration
```

## 🔐 Built-in Scripts

The backend directory includes several helper scripts for administration:
- `create_admin.py`: Create an initial administrator account.
- `create_test_users.py`: Populate the database with test users.
- `verify_mongo.py`: Test your MongoDB connection.

## 📄 License

This project is open-source. Please ensure you comply with the Terms of Service of any websites you scrape using this tool.
