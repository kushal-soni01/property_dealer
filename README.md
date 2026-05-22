# Broker

A full-stack real estate property management application built with Django REST API backend and React frontend.

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Project Structure](#project-structure)
- [Development](#development)
- [API Documentation](#api-documentation)

## 🎯 Project Overview

Broker is a comprehensive property management system that allows users to manage real estate properties, track localities, and manage infrastructure data. The application integrates with external APIs for enhanced functionality.

## 🛠 Tech Stack

### Backend
- **Framework**: Django 4.x
- **API**: Django REST Framework
- **Task Queue**: Celery
- **Cache/Message Broker**: Redis
- **CORS**: django-cors-headers
- **Environment**: python-dotenv

### Frontend
- **Framework**: React 18.x
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **HTTP Client**: Axios
- **Package Manager**: npm

### Database
- SQLite (Development)
- Supports migration to PostgreSQL/MySQL

## 📦 Prerequisites

- Python 3.8+
- Node.js 16+
- Redis Server
- pip and npm

## 🚀 Installation

### Backend Setup

1. **Create Virtual Environment**
```bash
cd backend
python -m venv venv
```

2. **Activate Virtual Environment**

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Create Environment File**
Create a `.env` file in the `backend` directory with the following variables:
```env
SECRET_KEY=your-django-secret-key
DEBUG=False
SERPAPI_API_KEY=your-serpapi-key
GROQ_API_KEY=your-groq-api-key
REDIS_URL=redis://127.0.0.1:6379
```

⚠️ **Security Note**: Never commit `.env` file to version control. Use `.gitignore` to exclude it.

5. **Run Migrations**
```bash
python manage.py migrate
```

6. **Create Superuser** (Optional)
```bash
python manage.py createsuperuser
```

### Frontend Setup

1. **Install Dependencies**
```bash
cd frontend
npm install
```

2. **Create Environment File** (if needed)
Create a `.env` file in the `frontend` directory:
```env
VITE_API_URL=http://localhost:8000
```

## 🔧 Configuration

### Environment Variables

The application requires the following environment variables in `.env`:

- **SECRET_KEY**: Django secret key for session management
- **DEBUG**: Debug mode (set to False in production)
- **SERPAPI_API_KEY**: API key for SerpAPI (location/search functionality)
- **GROQ_API_KEY**: API key for GROQ (AI functionality)
- **REDIS_URL**: Redis connection string (defaults to local Redis)

⚠️ **Never commit sensitive credentials to version control!**

## ▶️ Running the Application

### Backend Server

```bash
cd backend
python manage.py runserver
```

Backend runs on `http://localhost:8000`

### Frontend Development Server

```bash
cd frontend
npm run dev
```

Frontend runs on `http://localhost:5173`

### Running Celery (Background Tasks)

```bash
cd backend
celery -A core worker -l info
```

### Running Celery Beat (Scheduled Tasks)

```bash
cd backend
celery -A core beat -l info
```

## 📁 Project Structure

```
Broker/
├── backend/
│   ├── core/
│   │   ├── settings.py           # Django settings
│   │   ├── urls.py               # URL routing
│   │   ├── wsgi.py               # WSGI configuration
│   │   ├── asgi.py               # ASGI configuration
│   │   ├── celery.py             # Celery configuration
│   │   └── __init__.py
│   ├── properties/
│   │   ├── models.py             # Database models
│   │   ├── views.py              # API views
│   │   ├── serializers.py        # DRF serializers
│   │   ├── tasks.py              # Celery tasks
│   │   ├── admin.py              # Django admin
│   │   ├── tests.py              # Unit tests
│   │   ├── migrations/           # Database migrations
│   │   └── __init__.py
│   ├── manage.py
│   ├── requirements.txt          # Python dependencies
│   └── .env                      # Environment variables (not committed)
│
├── frontend/
│   ├── src/
│   │   ├── components/           # React components
│   │   ├── App.jsx               # Main App component
│   │   ├── main.jsx              # Entry point
│   │   └── index.css             # Global styles
│   ├── public/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js            # Vite configuration
│   ├── tailwind.config.js        # Tailwind CSS configuration
│   ├── postcss.config.js         # PostCSS configuration
│   └── .env                      # Environment variables (not committed)
│
├── .gitignore                    # Git ignore rules
├── README.md                     # This file
└── activate.bat                  # Activation script
```

## 👨‍💻 Development

### Backend Development

1. Make sure virtual environment is activated
2. Install development dependencies: `pip install -r requirements.txt`
3. Run migrations: `python manage.py migrate`
4. Start development server: `python manage.py runserver`

### Frontend Development

1. Install dependencies: `npm install`
2. Start dev server: `npm run dev`
3. Access at `http://localhost:5173`

### Building for Production

**Backend:**
```bash
python manage.py collectstatic
```

**Frontend:**
```bash
npm run build
```

Outputs to `frontend/dist/`

## 📚 API Documentation

### Base URL
```
http://localhost:8000/api/
```

### Available Endpoints

#### Properties
- `GET /api/properties/` - List all properties
- `POST /api/properties/` - Create new property
- `GET /api/properties/<id>/` - Retrieve property details
- `PUT /api/properties/<id>/` - Update property
- `DELETE /api/properties/<id>/` - Delete property

For detailed API documentation, visit `/api/` in your browser when the server is running.

## 🔐 Security Checklist

- [ ] `.env` file is in `.gitignore`
- [ ] `DEBUG=False` in production
- [ ] Generate new `SECRET_KEY` for production
- [ ] Never commit `db.sqlite3` to version control
- [ ] Configure CORS properly for production domains
- [ ] Use environment-specific settings
- [ ] Validate all user inputs
- [ ] Use HTTPS in production

## 📝 License

This project is private and proprietary.

## 🤝 Contributing

For contribution guidelines, please contact the project maintainer.

## 📞 Support

For issues and support, please create an issue in the repository.

---

**Last Updated**: May 2026
