# Loopy API

A secure, authenticated FastAPI-based backend service that provides a REST API for accessing CGM (Continuous Glucose Monitor) data from MongoDB. Built for DIY diabetes monitoring setups using the `loopy-basic` package.

## 🚀 Live API: https://loopy-api-production.up.railway.app

**Status**: ✅ Deployed and operational with Bearer token authentication

## Features ✅ Implemented

- **FastAPI Framework** - Modern, fast web framework with automatic API documentation
- **Authentication** - Bearer token security for medical data protection
- **MongoDB Integration** - Uses loopy-basic package with secure URI templating
- **Environment Configuration** - Secure MongoDB credential management
- **Type Safety** - Full type hints and Pydantic models
- **Railway Deployment** - Cloud deployment with environment variables
- **CORS Enabled** - Frontend integration ready for localhost development
- **JSON Serialization** - Proper handling of numpy/ObjectId types
- **Data Analysis** - Built-in glucose analysis and statistics

## Quick Start

### Prerequisites

- Python 3.12+
- uv (for dependency management)
- MongoDB Atlas account with CGM data

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/Waveform-Analytics/loopy-api.git
cd loopy-api
```

2. **Install dependencies:**
```bash
uv sync
```

3. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your MongoDB credentials
```

4. **Run the development server:**
```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

5. **Access the API:**
- API: http://localhost:8000
- Documentation: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

## API Endpoints

### Authentication Required
All CGM endpoints require Bearer token authentication:
```bash
Authorization: Bearer 5w6DXf7OSYtNl5wHHX_sSTViUmZfslMhjoAwOqtLZ0s
```

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/` | Root endpoint with service info | No |
| `GET` | `/health` | Health check endpoint | No |
| `GET` | `/api/cgm/current` | Get current glucose reading | **Yes** |
| `GET` | `/api/cgm/status` | Data availability status | **Yes** |
| `GET` | `/api/cgm/data?hours=24` | Get CGM data for specified hours | **Yes** |
| `GET` | `/api/cgm/analysis/{period}` | Get analysis (24h/week/month) | **Yes** |

## Example Usage

### Get Current Glucose Reading (Authentication Required)
```bash
# Local development
curl -H "Authorization: Bearer 5w6DXf7OSYtNl5wHHX_sSTViUmZfslMhjoAwOqtLZ0s" \
  http://localhost:8000/api/cgm/current

# Production API
curl -H "Authorization: Bearer 5w6DXf7OSYtNl5wHHX_sSTViUmZfslMhjoAwOqtLZ0s" \
  https://loopy-api-production.up.railway.app/api/cgm/current
```

**Response:**
```json
{
  "current_glucose": 142,
  "direction": "Flat",
  "trend": 4,
  "timestamp": "2025-01-16T10:30:00.000Z",
  "minutes_ago": 3.2,
  "device": "share2",
  "type": "sgv"
}
```

### Get 24-Hour Data with Analysis (Authentication Required)
```bash
# Local development
curl -H "Authorization: Bearer 5w6DXf7OSYtNl5wHHX_sSTViUmZfslMhjoAwOqtLZ0s" \
  "http://localhost:8000/api/cgm/data?hours=24"

# Production API
curl -H "Authorization: Bearer 5w6DXf7OSYtNl5wHHX_sSTViUmZfslMhjoAwOqtLZ0s" \
  "https://loopy-api-production.up.railway.app/api/cgm/data?hours=24"
```

**Response:**
```json
{
  "data": [
    {
      "datetime": "2025-01-16T10:30:00.000Z",
      "sgv": 142,
      "direction": "Flat",
      "glucose_category": "Normal"
    }
  ],
  "analysis": {
    "basic_stats": {
      "total_readings": 288,
      "avg_glucose": 145.2,
      "min_glucose": 71,
      "max_glucose": 324
    },
    "time_in_range": {
      "normal_percent": 72.5
    }
  },
  "time_range": {
    "start": "2025-01-15T10:30:00.000Z",
    "end": "2025-01-16T10:30:00.000Z",
    "hours": 24
  }
}
```

## Configuration

### Environment Variables

Create a `.env` file with your MongoDB credentials:

```env
# MongoDB Atlas Configuration (Secure Templating)
MONGODB_USERNAME=your_username
MONGODB_PW=your_password
MONGODB_URI_TEMPLATE=mongodb+srv://{username}:{password}@cluster.mongodb.net/?retryWrites=true&w=majority
MONGODB_DATABASE=myCGMitc

# Authentication
API_KEY=your_secure_api_key_here

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=false

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

## Docker Deployment

### Build and Run
```bash
# Build the image
docker build -t loopy-api .

# Run the container
docker run -p 8000:8000 --env-file .env loopy-api
```

### Docker Compose
```bash
docker-compose up -d
```

## Cloud Deployment ✅ Live on Railway

### Current Deployment
- **Platform**: Railway
- **URL**: https://loopy-api-production.up.railway.app
- **Repository**: Connected to GitHub main branch
- **Auto-deploy**: Enabled on git push
- **Environment**: All variables configured in Railway dashboard

### Setup Your Own Deployment

#### Railway (Recommended)
1. Fork the repository: https://github.com/Waveform-Analytics/loopy-api
2. Connect your GitHub repository to Railway
3. Set environment variables in Railway dashboard:
   - `MONGODB_USERNAME`
   - `MONGODB_PW` 
   - `MONGODB_URI_TEMPLATE`
   - `MONGODB_DATABASE`
   - `API_KEY`
4. Deploy automatically on push

### Other Options
- **Render**: Free tier available
- **Fly.io**: Good for containerized apps
- **DigitalOcean App Platform**: Simple deployment
- **AWS/Google Cloud**: Enterprise-grade hosting

## Testing

### Health Check (No Authentication)
```bash
# Local
curl http://localhost:8000/health

# Production
curl https://loopy-api-production.up.railway.app/health
```

### Data Status (Authentication Required)
```bash
# Local
curl -H "Authorization: Bearer 5w6DXf7OSYtNl5wHHX_sSTViUmZfslMhjoAwOqtLZ0s" \
  http://localhost:8000/api/cgm/status

# Production
curl -H "Authorization: Bearer 5w6DXf7OSYtNl5wHHX_sSTViUmZfslMhjoAwOqtLZ0s" \
  https://loopy-api-production.up.railway.app/api/cgm/status
```

### Analysis (Authentication Required)
```bash
# Local
curl -H "Authorization: Bearer 5w6DXf7OSYtNl5wHHX_sSTViUmZfslMhjoAwOqtLZ0s" \
  http://localhost:8000/api/cgm/analysis/24h

# Production
curl -H "Authorization: Bearer 5w6DXf7OSYtNl5wHHX_sSTViUmZfslMhjoAwOqtLZ0s" \
  https://loopy-api-production.up.railway.app/api/cgm/analysis/24h
```

## Security ✅ Implemented

- **Bearer Token Authentication** - All CGM endpoints protected
- **Environment-based configuration** - No hardcoded credentials
- **MongoDB URI templating** - Secure credential separation
- **CORS properly configured** - Frontend origins whitelisted
- **Input validation** - All endpoints validate parameters
- **Read-only database access** - No write operations
- **HTTPS in production** - Railway provides SSL certificates
- **JSON serialization security** - Proper handling of numpy/ObjectId types

## Development

### Install Development Dependencies
```bash
uv sync --group dev
```

### Code Formatting and Linting
```bash
# Format code
uv run ruff format

# Lint code
uv run ruff check
```

### Project Structure
```
loopy-api/
├── app/
│   ├── __init__.py
│   ├── main.py                # FastAPI app entry point
│   ├── api/                   # API routes
│   │   ├── __init__.py
│   │   ├── cgm.py            # CGM data endpoints (with auth)
│   │   └── health.py         # Health check endpoints
│   ├── core/                  # Core functionality
│   │   ├── __init__.py
│   │   ├── auth.py           # Bearer token authentication
│   │   ├── config.py         # Environment configuration
│   │   └── cors.py           # CORS settings
│   ├── models/                # Pydantic response models
│   │   ├── __init__.py
│   │   └── cgm.py            # CGM data models
│   └── services/              # Business logic
│       ├── __init__.py
│       └── cgm_service.py    # Uses loopy-basic package
├── notes/                     # Documentation
│   ├── API_BEGINNER_GUIDE.md
│   ├── AUTHENTICATION_GUIDE.md
│   ├── LOOPY_API_IMPLEMENTATION.md
│   └── WEB_APP_IMPLEMENTATION_PLAN.md
├── Dockerfile                 # Railway deployment
├── docker-compose.yml
├── pyproject.toml            # uv dependency management
├── uv.lock                   # Lock file
└── README.md
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Related Projects

- [loopy-basic](https://github.com/Waveform-Analytics/loopy-basic) - Core CGM data access library
- **loopy-web** - Frontend web application (next phase)

## For Frontend Developers

**Ready to integrate with your React/Vue/Angular app:**
- **API Base URL**: `https://loopy-api-production.up.railway.app`
- **API Key**: `5w6DXf7OSYtNl5wHHX_sSTViUmZfslMhjoAwOqtLZ0s`
- **CORS**: Configured for `localhost:3000` and `localhost:5173`
- **Documentation**: Available at `/docs` endpoint
- **Authentication**: Include `Authorization: Bearer <token>` header for CGM endpoints

## Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/Waveform-Analytics/loopy-api/issues) page
2. Create a new issue with details about your problem
3. Include your environment details and error messages
4. For authentication issues, verify your API key and endpoint URLs

---

**Built with ❤️ for the DIY diabetes community**