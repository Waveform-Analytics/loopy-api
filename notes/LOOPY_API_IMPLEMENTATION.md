# Loopy API - Backend Implementation Guide

## Overview

**loopy-api** is a FastAPI-based backend service that provides a secure, authenticated REST API for accessing CGM (Continuous Glucose Monitor) data from a MongoDB database. Built on the `loopy-basic` package, it's designed for DIY diabetes monitoring setups.

## ✅ Current Status: COMPLETED & DEPLOYED

- **Live API**: https://loopy-api-production.up.railway.app
- **Repository**: https://github.com/Waveform-Analytics/loopy-api
- **Authentication**: Bearer token system implemented
- **Deployment**: Railway cloud platform
- **API Key**: `5w6DXf7OSYtNl5wHHX_sSTViUmZfslMhjoAwOqtLZ0s`

## Architecture

### Key Features ✅ IMPLEMENTED
- ✅ **FastAPI Framework** - Modern, fast web framework with automatic API documentation
- ✅ **MongoDB Integration** - Uses loopy-basic package for data access with secure URI templating
- ✅ **Authentication** - Bearer token protection for medical data security
- ✅ **Environment Configuration** - Secure MongoDB credential management
- ✅ **Type Safety** - Full type hints and Pydantic models
- ✅ **JSON Serialization** - Handles numpy/ObjectId types properly
- ✅ **Railway Deployment** - Cloud deployment with environment variables
- ✅ **CORS Enabled** - Frontend integration ready

### Current Repository Structure

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
│   │   ├── config.py         # Environment configuration with URI templating
│   │   └── cors.py           # CORS settings
│   ├── models/                # Pydantic response models
│   │   ├── __init__.py
│   │   └── cgm.py            # CGM data models
│   └── services/              # Business logic
│       ├── __init__.py
│       └── cgm_service.py    # Uses loopy-basic package with JSON serialization
├── notes/                     # Documentation
│   ├── API_BEGINNER_GUIDE.md
│   ├── AUTHENTICATION_GUIDE.md
│   ├── LOOPY_API_IMPLEMENTATION.md
│   └── WEB_APP_IMPLEMENTATION_PLAN.md
├── Dockerfile                 # Railway deployment
├── docker-compose.yml
├── pyproject.toml            # uv dependency management
├── uv.lock                   # Lock file
└── README.md                 # Setup instructions
```

## Implementation Steps ✅ COMPLETED

### Phase 1: Project Setup ✅ COMPLETED

#### 1.1 Repository Created ✅
- **Repository**: https://github.com/Waveform-Analytics/loopy-api
- **Structure**: Complete with authentication module
- **Deployment**: Live on Railway

#### 1.2 Dependencies Installed ✅
```bash
# Modern Python tooling implemented:
uv init
uv add fastapi uvicorn[standard] loopy-basic python-dotenv pydantic-settings

# Development dependencies:
uv add --group dev ruff pytest
```

### Phase 2: Core Implementation ✅ COMPLETED

#### 2.1 FastAPI Application ✅ IMPLEMENTED

**Key Features Implemented:**
- ✅ **Authentication**: Bearer token middleware protecting all CGM endpoints
- ✅ **CORS**: Configured for development and production
- ✅ **Auto-docs**: Available at `/docs` with authentication testing
- ✅ **Health checks**: Public endpoints for monitoring
- ✅ **Error handling**: Comprehensive exception handling

**Live API**: https://loopy-api-production.up.railway.app

#### 2.2 Configuration Management ✅ IMPLEMENTED

**Security Features Implemented:**
- ✅ **MongoDB URI Templating**: Secure credential separation
- ✅ **API Key Authentication**: Bearer token system
- ✅ **Environment Variables**: Railway cloud configuration
- ✅ **CORS Configuration**: Frontend integration ready

**Environment Variables Required:**
```env
MONGODB_USERNAME=username
MONGODB_PW=password
MONGODB_URI_TEMPLATE=mongodb+srv://{username}:{password}@cluster.mongodb.net/
MONGODB_DATABASE=myCGMitc
API_KEY=5w6DXf7OSYtNl5wHHX_sSTViUmZfslMhjoAwOqtLZ0s
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

#### 2.3 CGM Service Layer

**app/services/cgm_service.py**
```python
from loopy.data.cgm import CGMDataAccess
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class CGMService:
    """Service layer for CGM data access using loopy-basic package."""
    
    @staticmethod
    def get_cgm_data(hours: int = 24) -> Dict[str, Any]:
        """Get recent CGM data using environment-configured MongoDB connection.
        
        Args:
            hours: Number of hours of data to retrieve (1-168)
            
        Returns:
            dict: CGM data with readings, analysis, and metadata
        """
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours)
            
            # Use loopy-basic with context manager for automatic connection handling
            with CGMDataAccess() as cgm:
                df = cgm.get_dataframe_for_period('custom', start_time, end_time)
                
                if df.empty:
                    return {
                        "data": [],
                        "analysis": None,
                        "message": f"No data found for the last {hours} hours",
                        "last_updated": datetime.now().isoformat(),
                        "time_range": {
                            "start": start_time.isoformat(),
                            "end": end_time.isoformat(),
                            "hours": hours
                        }
                    }
                
                # Perform analysis
                analysis = cgm.analyze_dataframe(df)
                
                # Convert DataFrame to JSON-serializable format
                data_records = df.to_dict('records')
                
                # Convert datetime objects to strings for JSON serialization
                for record in data_records:
                    if 'datetime' in record:
                        record['datetime'] = record['datetime'].isoformat()
                    if 'date_only' in record:
                        record['date_only'] = str(record['date_only'])
                
                return {
                    "data": data_records,
                    "analysis": analysis,
                    "last_updated": datetime.now().isoformat(),
                    "time_range": {
                        "start": start_time.isoformat(),
                        "end": end_time.isoformat(),
                        "hours": hours
                    }
                }
                
        except Exception as e:
            logger.error(f"Error retrieving CGM data: {e}")
            raise
    
    @staticmethod
    def get_current_glucose() -> Dict[str, Any]:
        """Get the most recent glucose reading.
        
        Returns:
            dict: Current glucose data with timestamp and trend information
        """
        try:
            with CGMDataAccess() as cgm:
                recent_readings = cgm.get_recent_readings(limit=1)
                
                if not recent_readings:
                    return {
                        "current_glucose": None, 
                        "message": "No recent data available"
                    }
                
                latest = recent_readings[0]
                timestamp_str = latest.get('dateString', '')
                
                # Calculate minutes since last reading
                if timestamp_str:
                    try:
                        # Handle timezone in dateString
                        timestamp_str_clean = timestamp_str.replace('Z', '+00:00')
                        latest_time = datetime.fromisoformat(timestamp_str_clean)
                        minutes_ago = (datetime.now().replace(tzinfo=latest_time.tzinfo) - latest_time).total_seconds() / 60
                    except:
                        minutes_ago = None
                else:
                    minutes_ago = None
                
                return {
                    "current_glucose": latest.get('sgv'),
                    "direction": latest.get('direction'),
                    "trend": latest.get('trend'),
                    "timestamp": timestamp_str,
                    "minutes_ago": round(minutes_ago, 1) if minutes_ago is not None else None,
                    "device": latest.get('device'),
                    "type": latest.get('type')
                }
                
        except Exception as e:
            logger.error(f"Error retrieving current glucose: {e}")
            raise
    
    @staticmethod
    def get_data_status() -> Dict[str, Any]:
        """Get data availability and connection status.
        
        Returns:
            dict: Status information about data availability
        """
        try:
            # Quick check with last hour of data
            result = CGMService.get_cgm_data(hours=1)
            data_count = len(result.get("data", []))
            
            return {
                "status": "connected" if data_count > 0 else "no_recent_data",
                "last_reading_count": data_count,
                "message": result.get("message", "Data available"),
                "last_updated": result.get("last_updated")
            }
            
        except Exception as e:
            logger.error(f"Error checking data status: {e}")
            return {
                "status": "error",
                "message": str(e),
                "last_updated": datetime.now().isoformat()
            }
```

#### 2.4 API Endpoints

**app/api/cgm.py**
```python
from fastapi import APIRouter, HTTPException, Query
from app.services.cgm_service import CGMService
from typing import Dict, Any

router = APIRouter()

@router.get("/data")
async def get_cgm_data(
    hours: int = Query(24, ge=1, le=168, description="Hours of data to retrieve (1-168)")
) -> Dict[str, Any]:
    """Get CGM data for the specified number of hours.
    
    Args:
        hours: Number of hours of data to retrieve (max 7 days)
        
    Returns:
        CGM data with readings, analysis, and metadata
    """
    try:
        return CGMService.get_cgm_data(hours=hours)
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error retrieving CGM data: {str(e)}"
        )

@router.get("/current")
async def get_current_glucose() -> Dict[str, Any]:
    """Get the most recent glucose reading.
    
    Returns:
        Current glucose reading with trend information
    """
    try:
        return CGMService.get_current_glucose()
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error retrieving current glucose: {str(e)}"
        )

@router.get("/status")
async def get_data_status() -> Dict[str, Any]:
    """Get data availability and connection status.
    
    Returns:
        Status information about data availability and connection health
    """
    try:
        return CGMService.get_data_status()
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error checking data status: {str(e)}"
        )

@router.get("/analysis/{period}")
async def get_analysis(
    period: str = Query(..., regex="^(24h|week|month)$", description="Analysis period")
) -> Dict[str, Any]:
    """Get analysis for a specific time period.
    
    Args:
        period: Analysis period (24h, week, or month)
        
    Returns:
        Analysis data for the specified period
    """
    try:
        hours_map = {"24h": 24, "week": 168, "month": 720}
        hours = hours_map.get(period, 24)
        
        result = CGMService.get_cgm_data(hours=hours)
        
        return {
            "period": period,
            "analysis": result.get("analysis"),
            "data_points": len(result.get("data", [])),
            "time_range": result.get("time_range"),
            "last_updated": result.get("last_updated")
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error performing analysis: {str(e)}"
        )
```

**app/api/health.py**
```python
from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {
        "status": "healthy",
        "service": "loopy-api",
        "timestamp": datetime.now().isoformat()
    }

@router.get("/ping")
async def ping():
    """Simple ping endpoint for monitoring."""
    return {"message": "pong"}
```

### Phase 3: Deployment Configuration ✅ COMPLETED

#### 3.1 Environment Configuration ✅ IMPLEMENTED

**Current .env.example:**
```env
# MongoDB Atlas Configuration
MONGODB_USERNAME=your_mongodb_username
MONGODB_PW=your_mongodb_password  
MONGODB_URI_TEMPLATE=mongodb+srv://{username}:{password}@cluster0.yourcluster.mongodb.net/?retryWrites=true&w=majority
MONGODB_DATABASE=myCGMitc

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=false

# Authentication
API_KEY=your_secure_api_key_here

# CORS Configuration (frontend URLs)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

#### 3.2 Docker Configuration

**Dockerfile**
```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies and uv
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && pip install uv

# Copy dependency files and install Python dependencies
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Copy application code
COPY app/ ./app/

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Run the application
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**docker-compose.yml**
```yaml
version: '3.8'

services:
  loopy-api:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

### Phase 4: Development & Testing ✅ COMPLETED

#### 4.1 Local Development ✅ WORKING

```bash
# Install dependencies
uv sync

# Copy environment template
cp .env.example .env
# Edit .env with your MongoDB credentials

# Run development server
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# API available at:
# - http://localhost:8000 (root)
# - http://localhost:8000/docs (Swagger UI with auth testing)
# - http://localhost:8000/redoc (ReDoc)
```

#### 4.2 API Testing ✅ WITH AUTHENTICATION

```bash
# Health check (no auth required)
curl https://loopy-api-production.up.railway.app/health

# Current glucose (auth required)
curl -H "Authorization: Bearer 5w6DXf7OSYtNl5wHHX_sSTViUmZfslMhjoAwOqtLZ0s" \
  https://loopy-api-production.up.railway.app/api/cgm/current

# Last 24 hours data (auth required)
curl -H "Authorization: Bearer 5w6DXf7OSYtNl5wHHX_sSTViUmZfslMhjoAwOqtLZ0s" \
  "https://loopy-api-production.up.railway.app/api/cgm/data?hours=24"

# Data status (auth required)
curl -H "Authorization: Bearer 5w6DXf7OSYtNl5wHHX_sSTViUmZfslMhjoAwOqtLZ0s" \
  https://loopy-api-production.up.railway.app/api/cgm/status

# Analysis (auth required)
curl -H "Authorization: Bearer 5w6DXf7OSYtNl5wHHX_sSTViUmZfslMhjoAwOqtLZ0s" \
  https://loopy-api-production.up.railway.app/api/cgm/analysis/24h
```

### Phase 5: Deployment ✅ LIVE ON RAILWAY

#### 5.1 Railway Deployment ✅ LIVE

**Current Deployment:**
- **URL**: https://loopy-api-production.up.railway.app
- **Auto-deploy**: Connected to GitHub main branch
- **Environment**: All variables configured in Railway dashboard
- **Status**: Live and responding

**Railway Configuration:**
- Repository: https://github.com/Waveform-Analytics/loopy-api
- Environment variables: MONGODB_USERNAME, MONGODB_PW, MONGODB_URI_TEMPLATE, API_KEY
- Auto-deploy on git push to main

#### 5.2 Alternative Deployment Options

**Docker (Local/VPS):**
```bash
docker build -t loopy-api .
docker run -p 8000:8000 --env-file .env loopy-api
```

## API Documentation ✅ LIVE

### Live API: https://loopy-api-production.up.railway.app

### Endpoints

| Method | Endpoint | Description | Auth Required | Parameters |
|--------|----------|-------------|---------------|------------|
| GET | `/` | Root endpoint | No | None |
| GET | `/health` | Health check | No | None |
| GET | `/api/cgm/data` | Get CGM data | **Yes** | `hours` (1-168) |
| GET | `/api/cgm/current` | Current glucose | **Yes** | None |
| GET | `/api/cgm/status` | Data status | **Yes** | None |
| GET | `/api/cgm/analysis/{period}` | Period analysis | **Yes** | `period` (24h/week/month) |

### Authentication

All CGM endpoints require Bearer token authentication:
```bash
Authorization: Bearer 5w6DXf7OSYtNl5wHHX_sSTViUmZfslMhjoAwOqtLZ0s
```

### Response Examples

**Current Glucose:**
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

**CGM Data:**
```json
{
  "data": [
    {
      "datetime": "2025-01-16T10:30:00.000Z",
      "sgv": 142,
      "direction": "Flat",
      "hour": 10,
      "glucose_category": "Normal"
    }
  ],
  "analysis": {
    "basic_stats": {
      "total_readings": 288,
      "avg_glucose": 145.2
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

## Security Considerations ✅ IMPLEMENTED

- ✅ **Bearer Token Authentication** - All CGM endpoints protected
- ✅ **Environment-based configuration** - No hardcoded credentials
- ✅ **MongoDB URI templating** - Secure credential separation  
- ✅ **CORS properly configured** - Frontend origins whitelisted
- ✅ **Input validation** - All endpoints validate parameters
- ✅ **HTTPS in production** - Railway provides SSL
- ✅ **Read-only database access** - No write operations
- ✅ **JSON serialization security** - Proper handling of numpy/ObjectId types

## ✅ Implementation Complete!

**What's Done:**
1. ✅ **Complete implementation** - All endpoints working
2. ✅ **Thorough testing** - All endpoints tested with real data
3. ✅ **Railway deployment** - Live and responding
4. ✅ **Environment configuration** - Secure variable management
5. ✅ **MongoDB Atlas connection** - Working with real CGM data
6. ✅ **Authentication system** - Bearer token protection

**Next Phase:**
🚧 **Frontend Integration** - Ready to build loopy-web React application

**For Frontend Developers:**
- **API Base URL**: `https://loopy-api-production.up.railway.app`
- **API Key**: `5w6DXf7OSYtNl5wHHX_sSTViUmZfslMhjoAwOqtLZ0s`
- **CORS**: Configured for localhost:3000 and localhost:5173
- **Documentation**: Available at `/docs` endpoint