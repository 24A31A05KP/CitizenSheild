# 🛡️ CitizenSheild - Women Safety Platform

[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)]()
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)]()
[![Flask](https://img.shields.io/badge/flask-2.3.3-red.svg)]()
[![PostgreSQL](https://img.shields.io/badge/postgresql-15.0-blue.svg)]()
[![Render](https://img.shields.io/badge/deployed-render-purple.svg)]()
[![GitHub Pages](https://img.shields.io/badge/deployed-github%20pages-brightgreen.svg)]()

## 📋 Overview

**CitizenSheild** is a comprehensive women safety platform that provides instant emergency assistance, location tracking, and safety resources. The platform enables users to trigger SOS alerts, share live location with trusted contacts, access emergency helplines, and report crimes anonymously.

### 🎯 Live Demo
- **Frontend:** https://24a31a05kp.github.io/CitizenSheild/
- **Backend API:** https://citizensheild.onrender.com
- **Health Check:** https://citizensheild.onrender.com/api/health

## ✨ Key Features

### 👤 User Features
- **🔐 User Authentication** - Secure JWT-based registration and login
- **🚨 SOS Alert System** - One-click emergency alerts with location sharing
- **📍 Live Location Tracking** - Share real-time location with trusted contacts
- **👥 Emergency Contacts** - Add and manage up to 5 emergency contacts
- **📞 Helpline Directory** - National emergency numbers (Police: 100, Women: 1091, Ambulance: 102)
- **📚 Safety Resources** - Self-defense tips, legal rights, and safety guides
- **📊 SOS History** - Track all past emergency alerts
- **👤 Profile Management** - Update personal information and preferences

### 👑 Admin Features
- **📈 Dashboard Analytics** - Real-time statistics dashboard
- **👥 User Management** - View and manage all registered users
- **🚨 SOS Monitoring** - Track all SOS alerts across the platform

## 🏗️ Technology Stack

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| Flask | 2.3.3 | Web framework |
| Flask-JWT-Extended | 4.5.2 | JWT authentication |
| psycopg2-binary | 2.9.9 | PostgreSQL adapter |
| bcrypt | 4.0.1 | Password hashing |
| python-dotenv | 1.0.0 | Environment configuration |
| Gunicorn | 21.2.0 | Production WSGI server |

### Frontend
- **HTML5** - Structure
- **CSS3** - Styling with responsive design
- **JavaScript (ES6+)** - Client-side logic
- **Leaflet.js** - Interactive maps for location tracking
- **FontAwesome** - Icons and visual elements

### Database
- **PostgreSQL 15** - Primary database (hosted on Render)
- Tables: users, emergency_contacts, sos_alerts, helplines, crime_reports

### Deployment
- **Frontend:** GitHub Pages
- **Backend:** Render.com
- **Database:** Render PostgreSQL

## 📁 Project Structure

\\\
CitizenSheild/
├── backend/
│   ├── core/
│   │   └── database.py          # PostgreSQL connection handler
│   ├── models/
│   │   ├── user.py               # User model operations
│   │   └── emergency_contact.py  # Emergency contact model
│   ├── utils/
│   │   └── validators.py         # Input validation utilities
│   ├── logs/                      # Application logs
│   ├── app.py                     # Main Flask application (1500+ lines)
│   └── .env                       # Environment variables
├── database/
│   └── schema.sql                 # PostgreSQL schema (9 tables)
├── frontend/
│   ├── css/
│   │   └── style.css              # Global styles
│   ├── js/
│   │   ├── api.js                 # API integration layer
│   │   ├── main.js                # Core functionality
│   │   └── navigation.js          # Navigation handling
│   ├── pages/
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── profile.html
│   │   ├── sos.html
│   │   ├── helplines.html
│   │   ├── safety-tips.html
│   │   ├── admin.html
│   │   └── crime-awareness/
│   │       ├── crime-map.html
│   │       ├── dashboard.html
│   │       ├── penalties.html
│   │       ├── report-crime.html
│   │       ├── resources.html
│   │       └── safety-assistant.html
│   ├── assets/
│   │   ├── icons/
│   │   └── images/
│   └── index.html                 # Landing page
├── requirements.txt               # Python dependencies
├── .gitignore
└── README.md
\\\

## 🚀 Local Development Setup

### Prerequisites
- Python 3.8 or higher
- PostgreSQL 15 or higher
- Git

### Step-by-Step Installation

#### 1. Clone the Repository
\\\ash
git clone https://github.com/24A31A05KP/CitizenSheild.git
cd CitizenSheild
\\\

#### 2. Create Virtual Environment
\\\ash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
\\\

#### 3. Install Dependencies
\\\ash
pip install -r requirements.txt
\\\

#### 4. Set Up PostgreSQL Database
\\\sql
-- Create database
CREATE DATABASE secureshe_db;

-- Import schema
psql -U postgres -d secureshe_db -f database/schema.sql
\\\

#### 5. Configure Environment Variables
Create \.env\ file in the \ackend/\ directory:
\\\env
# Database Configuration
DB_HOST=localhost
DB_NAME=secureshe_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_PORT=5432

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-key-change-this

# Application
PORT=5000
FLASK_ENV=development
\\\

#### 6. Run Backend Server
\\\ash
cd backend
python app.py
\\\
Server will run at: \http://localhost:5000\

#### 7. Serve Frontend
Open a new terminal:
\\\ash
cd frontend
# Using Python
python -m http.server 5500

# Or using VS Code Live Server extension
\\\
Access the app at: \http://localhost:5500\

## 🔌 API Endpoints

### Public Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | \/\ | API information |
| GET | \/api/health\ | Health check |
| GET | \/api/helplines\ | Get all helplines |

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | \/api/auth/register\ | Register new user |
| POST | \/api/auth/login\ | User login |
| POST | \/api/auth/refresh\ | Refresh JWT token |

### User Profile (Requires JWT)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | \/api/profile\ | Get user profile |
| PUT | \/api/profile/update\ | Update profile |
| POST | \/api/profile/contacts\ | Add emergency contact |
| DELETE | \/api/profile/contacts/<id>\ | Delete contact |
| PUT | \/api/profile/contacts/<id>/primary\ | Set primary contact |

### SOS System (Requires JWT)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | \/api/sos/trigger\ | Trigger SOS alert |
| GET | \/api/sos/history\ | Get SOS history |

### Admin Only (Requires Admin JWT)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | \/api/admin/stats\ | Dashboard statistics |
| GET | \/api/admin/users\ | List all users |
| GET | \/api/admin/sos-alerts\ | Get all SOS alerts |

## 💻 API Usage Examples

### Register User
\\\ash
curl -X POST https://citizensheild.onrender.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+919876543210",
    "password": "SecurePass@123"
  }'
\\\

### Login
\\\ash
curl -X POST https://citizensheild.onrender.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass@123"
  }'
\\\

### Trigger SOS
\\\ash
curl -X POST https://citizensheild.onrender.com/api/sos/trigger \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 28.6139,
    "longitude": 77.2090,
    "address": "New Delhi, India",
    "message": "Emergency! Need immediate assistance"
  }'
\\\

### Get Helplines
\\\ash
curl -X GET https://citizensheild.onrender.com/api/helplines
\\\

## 🗄️ Database Schema

### Core Tables
- **users** - User accounts (id, name, email, phone, password_hash, role)
- **emergency_contacts** - Trusted contacts (user_id, name, phone, is_primary)
- **sos_alerts** - Emergency alerts (user_id, location, status, timestamp)
- **helplines** - Emergency numbers (service_name, phone_number, country)
- **crime_reports** - Anonymous crime reports (type, location, description)
- **safety_tips** - Safety guidelines (category, title, content)
- **awareness_campaigns** - Safety campaigns and events

## 🔒 Security Features

- ✅ **Password Hashing** - bcrypt with salt rounds
- ✅ **JWT Authentication** - Stateless token-based auth
- ✅ **Input Validation** - Email, phone, password validation
- ✅ **SQL Injection Prevention** - Parameterized queries
- ✅ **CORS Protection** - Restricted allowed origins
- ✅ **Environment Variables** - No hardcoded secrets
- ✅ **Role-Based Access** - User and admin roles

## 🧪 Test Credentials

### Admin Account
- **Email:** admin@citizenshield.com
- **Password:** Admin@123

### Test User Account
- Register using the signup form
- Password must have 8+ chars, uppercase, lowercase, number, special char

## 📊 Current Deployment Status

| Service | Status | URL |
|---------|--------|-----|
| Frontend (GitHub Pages) | ✅ Live | https://24a31a05kp.github.io/CitizenSheild/ |
| Backend API (Render) | ✅ Live | https://citizensheild.onrender.com |
| Database (PostgreSQL) | ✅ Live | Hosted on Render |

## 🚦 Development Roadmap

### Completed ✅
- [x] User authentication system
- [x] SOS alert mechanism
- [x] Emergency contacts management
- [x] Helpline directory
- [x] Profile management
- [x] Admin dashboard
- [x] PostgreSQL database integration
- [x] Deployment to Render & GitHub Pages

### In Progress 🚧
- [ ] Real-time SMS notifications for SOS
- [ ] Email alerts for emergency contacts
- [ ] Live location tracking with WebSockets

### Planned 📅
- [ ] Mobile app (React Native)
- [ ] Voice-activated SOS
- [ ] AI-powered safety assistant
- [ ] Multi-language support
- [ ] Integration with local police stations
- [ ] Offline mode for emergencies

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. **Fork** the repository
2. **Create feature branch** (\git checkout -b feature/AmazingFeature\)
3. **Commit changes** (\git commit -m 'Add AmazingFeature'\)
4. **Push to branch** (\git push origin feature/AmazingFeature\)
5. **Open Pull Request**

### Development Guidelines
- Follow PEP 8 for Python code
- Use meaningful commit messages
- Update documentation for new features
- Test thoroughly before submitting PR

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Contributors

- **ILLA SAI BHARAT KUMAR** - Lead Developer
- GitHub: [@24A31A05KP](https://github.com/24A31A05KP)

## 🙏 Acknowledgments

- Flask and PostgreSQL communities
- Render for free backend hosting
- GitHub Pages for frontend hosting
- All contributors and testers

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/24A31A05KP/CitizenSheild/issues)
- **Email:** illasaibharatkumar@gmail.com
- **Documentation:** [Project Wiki](https://github.com/24A31A05KP/CitizenSheild/wiki)

## ⚠️ Disclaimer

This platform is designed to supplement, not replace, official emergency services. In life-threatening situations, always contact your local emergency number (100 for police, 102 for ambulance, 1091 for women's helpline) directly. The developers assume no liability for misuse or delays in emergency response.

---

## 🎯 Quick Commands Reference

\\\ash
# Clone and setup
git clone https://github.com/24A31A05KP/CitizenSheild.git
cd CitizenSheild

# Backend setup
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
cd backend
python app.py

# Frontend (new terminal)
cd frontend
python -m http.server 5500

# Git commands
git add .
git commit -m "Your message"
git push origin main
\\\

---

**Made with ❤️ for women safety** | **CitizenSheild v2.0.0**

[Report Bug](https://github.com/24A31A05KP/CitizenSheild/issues) · [Request Feature](https://github.com/24A31A05KP/CitizenSheild/issues) · [Live Demo](https://24a31a05kp.github.io/CitizenSheild/)
