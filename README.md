# Loopy API

A FastAPI-based backend service that provides a REST API for accessing CGM (Continuous Glucose Monitor) data from MongoDB. Built for DIY diabetes monitoring setups using the `loopy-basic` package.

## Features

- FastAPI Framework - Modern, fast web framework with automatic API documentation
- MongoDB Integration - Uses loopy-basic package for seamless data access
- Environment Configuration - Secure MongoDB credential management
- Type Safety - Full type hints and Pydantic models
- Docker Ready - Container deployment with minimal configuration
- CORS Enabled - Frontend integration ready
- Data Analysis - Built-in glucose analysis and statistics

## Quick Start

### Prerequisites

- Python 3.12+
- uv (for dependency management)
- MongoDB Atlas account with CGM data

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/loopy-api.git
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

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Root endpoint with service info |
| `GET` | `/api/health` | Health check endpoint |
| `GET` | `/api/ping` | Simple ping for monitoring |
| `GET` | `/api/cgm/current` | Get current glucose reading |
| `GET` | `/api/cgm/status` | Data availability status |
| `GET` | `/api/cgm/data?hours=24` | Get CGM data for specified hours |
| `GET` | `/api/cgm/analysis/{period}` | Get analysis (24h/week/month) |

## Example Usage

### Get Current Glucose Reading
```bash
curl http://localhost:8000/api/cgm/current
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

### Get 24-Hour Data with Analysis
```bash
curl "http://localhost:8000/api/cgm/data?hours=24"
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
# MongoDB Atlas Configuration
MONGODB_USERNAME=your_username
MONGODB_PW=your_password
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
MONGODB_DATABASE=myCGMitc

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

## Cloud Deployment

### Railway (Recommended)
1. Connect your GitHub repository to Railway
2. Set environment variables in the Railway dashboard
3. Deploy automatically on push

### Other Options
- **Render**: Free tier available
- **Fly.io**: Good for containerized apps
- **DigitalOcean App Platform**: Simple deployment
- **AWS/Google Cloud**: Enterprise-grade hosting

## Testing

### Health Check
```bash
curl http://localhost:8000/api/health
```

### Data Status
```bash
curl http://localhost:8000/api/cgm/status
```

### Analysis
```bash
curl http://localhost:8000/api/cgm/analysis/24h
```

## Security

- Environment-based configuration (no hardcoded credentials)
- CORS properly configured for frontend origins
- Input validation on all endpoints
- Read-only database access
- HTTPS required in production

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
│   │   ├── cgm.py            # CGM data endpoints
│   │   └── health.py         # Health check endpoints
│   ├── core/                  # Core functionality
│   │   ├── __init__.py
│   │   └── config.py         # Environment configuration
│   ├── models/                # Pydantic response models
│   │   ├── __init__.py
│   │   └── cgm.py            # CGM data models
│   └── services/              # Business logic
│       ├── __init__.py
│       └── cgm_service.py    # Uses loopy-basic package
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── .env.example
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

- [loopy-basic](https://github.com/yourusername/loopy-basic) - Core CGM data access library
- [loopy-web](https://github.com/yourusername/loopy-web) - Frontend web application

## Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/yourusername/loopy-api/issues) page
2. Create a new issue with details about your problem
3. Include your environment details and error messages

---

**Built with ❤️ for the DIY diabetes community**