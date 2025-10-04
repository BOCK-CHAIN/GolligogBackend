# Golligog Search Engine - Technical Documentation

A comprehensive, privacy-focused search engine with cross-platform applications and Google-only results.

## 📚 Documentation Structure

This documentation provides complete technical coverage of the Golligog Search Engine system, including architecture, development, deployment, and maintenance guides.

### 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Golligog Search Engine                  │
├─────────────────────────────────────────────────────────────┤
│  Frontend Applications                                      │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────┐│
│  │   Flutter   │ │    Web      │ │   Mobile    │ │Desktop ││
│  │     App     │ │Application  │ │    Apps     │ │  Apps  ││
│  └─────────────┘ └─────────────┘ └─────────────┘ └────────┘│
├─────────────────────────────────────────────────────────────┤
│  Backend Services                                           │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────┐│
│  │   Node.js   │ │   Flask     │ │   SearXNG   │ │   JWT  ││
│  │  Auth API   │ │   Proxy     │ │   Engine    │ │  Auth  ││
│  └─────────────┘ └─────────────┘ └─────────────┘ └────────┘│
├─────────────────────────────────────────────────────────────┤
│  Data Layer                                                 │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────┐│
│  │ PostgreSQL  │ │   Prisma    │ │   Google    │ │  Cache ││
│  │  Database   │ │    ORM      │ │Search APIs  │ │ Layer  ││
│  └─────────────┘ └─────────────┘ └─────────────┘ └────────┘│
└─────────────────────────────────────────────────────────────┘
```

## 📖 Documentation Sections

### 1. [System Overview](./01-system-overview.md)
- Project architecture and components
- Technology stack and dependencies
- System requirements and compatibility
- Key features and capabilities

### 2. [Backend Development](./02-backend-development.md)
- Node.js authentication server setup
- Flask search proxy configuration
- Database schema and migrations
- API endpoints and authentication

### 3. [SearXNG Configuration](./03-searxng-configuration.md)
- Installation and setup guide
- Google-only search configuration
- Privacy and security settings
- Performance optimization

### 4. [Frontend Development](./04-frontend-development.md)
- Flutter application architecture
- Cross-platform development
- UI/UX implementation
- State management and services

### 5. [Deployment Guide](./05-deployment-guide.md)
- AWS infrastructure setup
- Container orchestration
- Domain and SSL configuration
- CI/CD pipeline implementation

### 6. [API Reference](./06-api-reference.md)
- Authentication endpoints
- Search API documentation
- User management APIs
- Error codes and responses

### 7. [Development Workflow](./07-development-workflow.md)
- Local development setup
- Testing strategies
- Code quality standards
- Git workflow and contribution

### 8. [Monitoring & Maintenance](./08-monitoring-maintenance.md)
- System monitoring setup
- Performance metrics
- Log management
- Backup and recovery

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Flutter SDK 3.9+
- Python 3.9+
- PostgreSQL 15+
- Docker and Docker Compose

### Local Development Setup
```bash
# Clone the repository
git clone https://github.com/DarshanCHMSR/search-engine.git
cd search-engine

# Setup backend services
cd server && npm install
cd ../backend && pip install -r requirements.txt

# Setup Flutter app
cd flutter/search_engine_app && flutter pub get

# Configure environment
cp server/.env.example server/.env
# Edit .env with your configuration

# Start services
docker-compose up -d  # Database and SearXNG
npm run dev          # Backend API
flutter run          # Frontend app
```

## 🔧 Technology Stack

### Frontend
- **Framework**: Flutter 3.9+ (Dart)
- **Platforms**: Android, iOS, Web, Windows, macOS, Linux
- **State Management**: Provider pattern
- **HTTP Client**: Dart HTTP package
- **Storage**: SharedPreferences, Hive

### Backend
- **Authentication Server**: Node.js, Express.js, Prisma ORM
- **Search Proxy**: Python Flask, CORS handling
- **Database**: PostgreSQL with connection pooling
- **Authentication**: JWT tokens, bcrypt hashing

### Search Engine
- **Core Engine**: SearXNG (Python-based meta-search)
- **Search Sources**: Google-only configuration
- **Privacy**: No tracking, source information filtered
- **Performance**: Cached results, optimized queries

### Infrastructure
- **Cloud Platform**: Amazon Web Services (AWS)
- **Containers**: Docker, Amazon ECS
- **Database**: Amazon RDS PostgreSQL
- **Storage**: Amazon S3, CloudFront CDN
- **Monitoring**: CloudWatch, Application logs

## 📊 Performance Metrics

### Search Performance
- **Average Response Time**: < 800ms
- **Search Accuracy**: Google-quality results
- **Uptime Target**: 99.9%
- **Concurrent Users**: 1000+ supported

### Application Performance
- **Flutter App Size**: < 50MB (all platforms)
- **Startup Time**: < 3 seconds
- **Memory Usage**: < 100MB typical
- **Battery Optimization**: Background processing minimized

## 🔒 Security Features

### Data Protection
- **End-to-End Encryption**: All API communications
- **Authentication**: JWT-based with refresh tokens
- **Privacy**: No search query logging
- **GDPR Compliance**: User data protection

### Infrastructure Security
- **Network**: VPC with private subnets
- **Access Control**: IAM roles and policies
- **SSL/TLS**: Certificate Manager integration
- **Secrets**: AWS Secrets Manager

## 🌍 Supported Platforms

### Mobile Applications
- **Android**: API level 21+ (Android 5.0+)
- **iOS**: iOS 12.0+ (iPhone 6s and newer)
- **Distribution**: Google Play Store, Apple App Store

### Desktop Applications
- **Windows**: Windows 10 version 1903+
- **macOS**: macOS 10.14 Mojave+
- **Linux**: Ubuntu 18.04+, Fedora 33+

### Web Application
- **Browsers**: Chrome 88+, Firefox 85+, Safari 14+, Edge 88+
- **Progressive Web App**: Offline support, installable
- **Responsive Design**: Mobile and desktop optimized

## 📞 Support & Contributing

### Getting Help
- **Documentation**: Comprehensive guides in `/docs`
- **Issues**: GitHub Issues for bug reports
- **Discussions**: GitHub Discussions for questions

### Contributing
1. Fork the repository
2. Create a feature branch
3. Follow coding standards
4. Add tests for new features
5. Submit a pull request

### Development Standards
- **Code Quality**: ESLint, Dart Analysis
- **Testing**: Unit tests, integration tests
- **Documentation**: Inline comments, README updates
- **Commits**: Conventional commit messages

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

## 🔄 Version History

- **v1.0.0** (Current): Initial release with core functionality
- **Roadmap**: Multi-language support, advanced filters, AI integration

---

*Last updated: September 2025*
