# AIOne Scraper 🚀

A comprehensive, web scraping built with React, Flask, and MongoDB. AIOne Scraper provides a powerful dashboard to extract, view, and manage data from multiple platforms including Reddit, Instagram, YouTube, LinkedIn, OpenTable, Google Maps, and more.

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
<img width="1875" height="890" alt="image" src="https://github.com/user-attachments/assets/72e4056b-8c9c-4fa6-b773-1337b9f5f3ad" />
<img width="1879" height="903" alt="image" src="https://github.com/user-attachments/assets/d5bf6d72-6c86-4c71-bb60-20b9a24765c3" />


### Option 2: Running with Docker

If you have Docker Desktop installed, you can start the entire stack (Frontend, Backend, Database, and Caddy Web Server) with a single command:

```bash
docker-compose up -d --build
```
*(If using the newer Docker CLI, use `docker compose up -d --build`)*

 <img width="1919" height="915" alt="image" src="https://github.com/user-attachments/assets/741d42f2-708e-4d47-86bf-cbc4005f0d70" />
 <img width="1911" height="914" alt="image" src="https://github.com/user-attachments/assets/398e8c01-7798-4eab-a7ef-d32b2b0bbd11" />
 <img width="1919" height="910" alt="image" src="https://github.com/user-attachments/assets/a102cf54-c8fb-4253-b3b2-f9fad55bca9f" />
 <img width="1906" height="915" alt="image" src="https://github.com/user-attachments/assets/0a89a947-0afa-47f9-a9ea-880995544ba7" />




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
