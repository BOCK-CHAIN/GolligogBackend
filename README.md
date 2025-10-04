# Golligog Search Engine

A modern, privacy-focused search engine built with Flutter frontend and Node.js backend, using SearXNG as the search provider.

## 🌟 Features

### Search Engine
- **Multi-category search**: All, Images, Videos, News, Maps, Books, Scholar
- **SearXNG integration**: Privacy-focused meta-search engine
- **Google-like UI**: Clean, intuitive interface
- **Responsive design**: Works on all screen sizes
- **URL launching**: Open search results in browser

### Authentication System
- **User registration/login**: Secure authentication with JWT
- **Password encryption**: bcrypt with configurable salt rounds
- **Profile management**: User preferences and settings
- **Session management**: Secure cookie-based sessions

### Backend Features
- **RESTful API**: Express.js with comprehensive endpoints
- **Database**: PostgreSQL with Sequelize ORM
- **Security**: Helmet, CORS, rate limiting
- **Validation**: Input validation and sanitization
- **Error handling**: Comprehensive error management

## 🏗️ Architecture

```
golligog/
├── flutter/                    # Flutter mobile app
│   └── search_engine_app/
│       ├── lib/
│       │   ├── main.dart      # App entry point
│       │   ├── auth_wrapper.dart   # Authentication UI
│       │   ├── login_page.dart     # Login form
│       │   ├── signup_page.dart    # Registration form
│       │   ├── search_results_page.dart  # Search results display
│       │   ├── services/
│       │   │   ├── searxng_service.dart  # SearXNG API client
│       │   │   └── auth_service.dart     # Authentication API client
│       │   └── models/
│       │       └── search_models.dart    # Data models
│       └── pubspec.yaml       # Flutter dependencies
├── server/                    # Node.js backend
│   ├── server.js             # Server entry point
│   ├── config/
│   │   └── database.js       # Database configuration
│   ├── models/
│   │   └── User.js          # User model
│   ├── routes/
│   │   ├── auth.js          # Authentication routes
│   │   └── user.js          # User management routes
│   ├── middleware/
│   │   ├── auth.js          # JWT authentication middleware
│   │   └── errorHandler.js  # Error handling middleware
│   ├── package.json         # Node.js dependencies
│   ├── .env.example         # Environment template
│   └── .env                 # Environment variables
└── README.md                # This file
```

## 🚀 Getting Started

### Prerequisites
- Flutter SDK 3.9+
- Node.js 16+
- PostgreSQL database
- SearXNG instance (optional, uses public instances by default)

### Backend Setup

1. **Navigate to server directory**:
   ```bash
   cd server
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

4. **Environment variables**:
   ```env
   NODE_ENV=development
   PORT=5000
   
   # Database (AWS RDS PostgreSQL)
   DB_HOST=your-rds-endpoint.region.rds.amazonaws.com
   DB_PORT=5432
   DB_NAME=golligog_db
   DB_USER=your_username
   DB_PASSWORD=your_password
   
   # JWT Configuration
   JWT_SECRET=your_super_secret_jwt_key
   JWT_EXPIRE=7d
   
   # Security
   BCRYPT_SALT_ROUNDS=12
   ```

5. **Start the server**:
   ```bash
   npm run dev  # Development with nodemon
   # or
   npm start    # Production
   ```

### Flutter App Setup

1. **Navigate to Flutter directory**:
   ```bash
   cd flutter/search_engine_app
   ```

2. **Install dependencies**:
   ```bash
   flutter pub get
   ```

3. **Run the app**:
   ```bash
   flutter run
   ```

## 📱 Usage

### Search Features
1. **Homepage**: Google-like search interface
2. **Search categories**: Select from All, Images, Videos, News, Maps, Books, Scholar
3. **Results**: Specialized layouts for different content types
4. **External links**: Tap results to open in browser

### Authentication
1. **Sign up**: Create account with email, username, and password
2. **Sign in**: Login with email and password
3. **Profile**: Manage user preferences and settings

## 🔧 API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/me` - Get current user
- `POST /api/auth/refresh` - Refresh JWT token

### User Management
- `GET /api/user/profile` - Get user profile
- `PUT /api/user/profile` - Update profile
- `PUT /api/user/preferences` - Update preferences
- `PUT /api/user/password` - Change password
- `DELETE /api/user/account` - Deactivate account
- `GET /api/user/stats` - Get user statistics

## 🛡️ Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: bcrypt with configurable salt rounds
- **Rate Limiting**: Prevents abuse and DoS attacks
- **Input Validation**: Server-side validation with express-validator
- **CORS Protection**: Configurable cross-origin resource sharing
- **Security Headers**: Helmet.js for security headers
- **SQL Injection Protection**: Sequelize ORM with parameterized queries

## 🗄️ Database Schema

### Users Table
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  username VARCHAR(50) UNIQUE NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL,
  first_name VARCHAR(50) NOT NULL,
  last_name VARCHAR(50) NOT NULL,
  is_active BOOLEAN DEFAULT true,
  is_verified BOOLEAN DEFAULT false,
  last_login TIMESTAMP,
  profile_picture VARCHAR(500),
  preferences JSONB DEFAULT '{"searchEngine":"google","resultsPerPage":10,"safeSearch":true,"theme":"light"}',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

## 🔍 SearXNG Integration

The app integrates with SearXNG for privacy-focused search:

- **Multiple engines**: Aggregates results from various search engines
- **No tracking**: Privacy-focused search without user tracking
- **Categories**: Support for different content types
- **Customizable**: Can use custom SearXNG instances

## 📦 Dependencies

### Flutter
- **http**: ^1.1.0 - HTTP client for API calls
- **url_launcher**: ^6.3.2 - Launch URLs in browser

### Node.js
- **express**: ^4.18.2 - Web framework
- **sequelize**: ^6.33.0 - Database ORM
- **bcryptjs**: ^2.4.3 - Password hashing
- **jsonwebtoken**: ^9.0.2 - JWT tokens
- **cors**: ^2.8.5 - CORS handling
- **helmet**: ^7.0.0 - Security headers
- **express-validator**: ^7.0.1 - Input validation

## 🚢 Deployment

### Backend (AWS/Heroku)
1. Set up PostgreSQL database (AWS RDS)
2. Configure environment variables
3. Deploy to cloud platform
4. Set up domain and SSL

### Frontend (Mobile)
1. Build for production: `flutter build apk`
2. Distribute via app stores or direct download

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **SearXNG**: Privacy-focused meta-search engine
- **Flutter**: Cross-platform mobile framework
- **Express.js**: Fast, unopinionated web framework
- **PostgreSQL**: Advanced open-source database

## 📞 Support

For support, email support@golligog.com or create an issue on GitHub.

---

**Made with ❤️ by the Golligog Team**
