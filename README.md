# Broker

A full-stack real estate property management application built with a Django REST API backend and React frontend, now featuring admin-side location autocomplete with coordinate auto-fill for faster locality entry.

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

Broker is a comprehensive property management system that allows users to manage real estate properties, track localities, and manage infrastructure data. It integrates external APIs for enhanced functionality and includes an admin autocomplete workflow that:

- Fetches location suggestions from SerpAPI.
- Displays a dropdown of matching places.
- Auto-fills latitude/longitude to 6 decimal places.
- Allows manual entry when APIs are unavailable.

### Admin Autocomplete Architecture

The admin autocomplete feature is implemented as a custom Django form widget wired into the Locality admin form:

- **Widget**: `LocationAutocompleteWidget` renders an input plus inline JS/CSS for dropdown behavior.
- **Data flow**: Typing in the Location field calls a backend endpoint that proxies SerpAPI results into a normalized response.
- **APIs used**: SerpAPI Google Maps (`engine=google_maps`, `type=search`) to fetch place suggestions and coordinates.
- **Fallbacks**: If the API is unavailable or returns no matches, the UI shows a message and allows manual entry.
- **Autofill**: Selected items populate latitude/longitude fields and format them to 6 decimal places.
- **Parsing**: Supports multiple SerpAPI response shapes (`local_results`, `places`, `knowledge_graph`, `gps_coordinates`, `geometry.location`).

## 🛠 Tech Stack

### Backend

- **Framework**: Django 5.2.x
- **API**: Django REST Framework
- **Task Queue**: Celery
- **Cache/Message Broker**: Redis
- **CORS**: django-cors-headers
- **Environment**: python-dotenv
- **Admin UX**: Custom autocomplete widget for locality location

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
DEBUG=True
SERPAPI_API_KEY=your-serpapi-key
GROQ_API_KEY=your-groq-api-key
REDIS_URL=redis://default:password@host:port
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
- **DEBUG**: Debug mode (True for local development to serve admin static files)
- **SERPAPI_API_KEY**: API key for SerpAPI (location/search functionality)
- **GROQ_API_KEY**: API key for GROQ (AI functionality)
- **REDIS_URL**: Redis connection string (defaults to local Redis)

⚠️ **Never commit sensitive credentials to version control!**

## ▶️ Running the Application

### Backend Server

```bash
cd backend/core
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
cd backend/core
celery -A core worker -l info --pool=solo
```

### Running Celery Beat (Scheduled Tasks)

```bash
cd backend/core
celery -A core beat -l info --pool=solo
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
│   │   ├── widgets.py            # Location autocomplete widget
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
4. Collect static files (admin assets): `python manage.py collectstatic --clear --noinput`
5. Start development server: `python manage.py runserver`

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

#### Autocomplete

- `GET /api/autocomplete-location/?q=<query>&city=<city>` - Location suggestions for admin autocomplete
- `GET /api/get-coordinates/?location=<location>&city=<city>` - Coordinate lookup (fallback)

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
