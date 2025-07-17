# Securing Your Loopy API: Authentication Guide

## Why Secure Your API?

Your CGM data is **medical information** that should be private. Without authentication, anyone who discovers your API URL can access your glucose readings, patterns, and health data.

## Authentication Options (Simple to Complex)

### 1. API Key Authentication (Recommended)
- **How it works**: Like a password for your API
- **Pros**: Simple, similar to Nightscout
- **Cons**: If key is leaked, need to change it everywhere
- **Best for**: Personal use, sharing with family/close friends

### 2. Multiple API Keys
- **How it works**: Different keys for different users/apps
- **Pros**: Can revoke individual access
- **Cons**: More management overhead
- **Best for**: Sharing with multiple people/apps

### 3. JWT Tokens (Advanced)
- **How it works**: Time-limited tokens, more secure
- **Pros**: Very secure, tokens expire
- **Cons**: More complex to implement
- **Best for**: Production apps, many users

## Implementation: API Key Authentication

### Step 1: Add Authentication to Your API

Create a new file for authentication:

```python
# app/core/auth.py
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings
import secrets

security = HTTPBearer()

def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify the API key from the Authorization header."""
    if credentials.credentials != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials

# Optional: Support multiple API keys
def verify_multi_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify API key against multiple allowed keys."""
    allowed_keys = settings.api_keys.split(',')  # Comma-separated keys
    if credentials.credentials not in allowed_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials
```

### Step 2: Update Configuration

Add API key settings to your config:

```python
# app/core/config.py
from pydantic_settings import BaseSettings
from typing import Optional
import secrets

class Settings(BaseSettings):
    """Application settings from environment variables."""
    
    # MongoDB connection (from environment variables)
    mongodb_username: str
    mongodb_pw: str  
    mongodb_uri: str
    mongodb_database: str = "myCGMitc"
    
    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = False
    
    # Authentication
    api_key: str = secrets.token_urlsafe(32)  # Generate random key if not provided
    api_keys: str = ""  # Optional: comma-separated list for multiple keys
    
    # CORS settings
    cors_origins: str = "http://localhost:3000,http://localhost:5173"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
```

### Step 3: Protect Your Endpoints

Update your API endpoints to require authentication:

```python
# app/api/cgm.py
from fastapi import APIRouter, HTTPException, Query, Depends
from app.services.cgm_service import CGMService
from app.core.auth import verify_api_key  # Add this import
from typing import Dict, Any

router = APIRouter()

@router.get("/data")
async def get_cgm_data(
    hours: int = Query(24, ge=1, le=168, description="Hours of data to retrieve (1-168)"),
    _: str = Depends(verify_api_key)  # Add this line
) -> Dict[str, Any]:
    """Get CGM data for the specified number of hours."""
    try:
        return CGMService.get_cgm_data(hours=hours)
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error retrieving CGM data: {str(e)}"
        )

@router.get("/current")
async def get_current_glucose(
    _: str = Depends(verify_api_key)  # Add this line
) -> Dict[str, Any]:
    """Get the most recent glucose reading."""
    try:
        return CGMService.get_current_glucose()
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error retrieving current glucose: {str(e)}"
        )

@router.get("/status")
async def get_data_status(
    _: str = Depends(verify_api_key)  # Add this line
) -> Dict[str, Any]:
    """Get data availability and connection status."""
    try:
        return CGMService.get_data_status()
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error checking data status: {str(e)}"
        )

@router.get("/analysis/{period}")
async def get_analysis(
    period: str,
    _: str = Depends(verify_api_key)  # Add this line
) -> Dict[str, Any]:
    """Get analysis for a specific time period."""
    try:
        # Validate period parameter
        valid_periods = {"24h": 24, "week": 168, "month": 720}
        if period not in valid_periods:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid period '{period}'. Must be one of: {', '.join(valid_periods.keys())}"
            )
        
        hours = valid_periods[period]
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

### Step 4: Keep Health Endpoint Public

Keep the health endpoint public (no authentication) for monitoring:

```python
# app/api/health.py - NO CHANGES NEEDED
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

## Setting Up Authentication by Platform

### Railway Setup

1. **Deploy your updated code**:
```bash
git add .
git commit -m "Add API key authentication"
git push origin main
```

2. **Set environment variables in Railway**:
   - Go to your Railway project
   - Click "Variables" tab
   - Add these variables:
     - `API_KEY` = `your-secret-key-here` (generate a strong one!)
     - `MONGODB_USERNAME` = your MongoDB username
     - `MONGODB_PW` = your MongoDB password
     - `MONGODB_URI` = your MongoDB connection string
     - `MONGODB_DATABASE` = myCGMitc

3. **Generate a secure API key**:
```bash
# Generate a random 32-character API key
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
# Example output: kJ8HfX2N9mP5qR7sT1vW3yZ4aB6cD8eF9gH0iJ2kL4mN6oP8qR
```

### Render Setup

1. **Deploy your code**:
   - Push to GitHub as above
   - Render will auto-deploy

2. **Set environment variables in Render**:
   - Go to your Render dashboard
   - Click your service → "Environment"
   - Add the same variables as Railway

### Fly.io Setup

1. **Set secrets**:
```bash
fly secrets set API_KEY=your-secret-key-here
fly secrets set MONGODB_USERNAME=your_username
fly secrets set MONGODB_PW=your_password
fly secrets set MONGODB_URI=your_connection_string
fly secrets set MONGODB_DATABASE=myCGMitc
```

2. **Deploy**:
```bash
fly deploy
```

## How to Use Your Secured API

### With curl
```bash
# Before (unsecured)
curl https://your-api.railway.app/api/cgm/current

# After (secured)
curl -H "Authorization: Bearer your-secret-key-here" https://your-api.railway.app/api/cgm/current
```

### With JavaScript (Web App)
```javascript
const API_KEY = 'your-secret-key-here';
const API_URL = 'https://your-api.railway.app';

async function getCurrentGlucose() {
    const response = await fetch(`${API_URL}/api/cgm/current`, {
        headers: {
            'Authorization': `Bearer ${API_KEY}`
        }
    });
    
    if (!response.ok) {
        throw new Error('Authentication failed');
    }
    
    return await response.json();
}
```

### With Python
```python
import requests

API_KEY = 'your-secret-key-here'
API_URL = 'https://your-api.railway.app'

headers = {
    'Authorization': f'Bearer {API_KEY}'
}

response = requests.get(f'{API_URL}/api/cgm/current', headers=headers)
data = response.json()
```

## Sharing Your API with Others

### Option 1: Single API Key (Simple)

**For family/close friends:**
1. Give them your API URL: `https://your-api.railway.app`
2. Give them your API key: `your-secret-key-here`
3. Show them how to use it in their apps

**Pros**: Simple to set up
**Cons**: If someone shares the key, you have to change it everywhere

### Option 2: Multiple API Keys (Recommended)

**Update your environment variables:**
```bash
# In Railway/Render/Fly.io
API_KEYS=key1-for-family,key2-for-doctor,key3-for-friend,key4-for-app
```

**Generate individual keys:**
```bash
# Generate multiple keys
python3 -c "
import secrets
for i in range(5):
    print(f'Key {i+1}: {secrets.token_urlsafe(32)}')
"
```

**Keep a record:**
```
Key 1 (Family): kJ8HfX2N9mP5qR7sT1vW3yZ4aB6cD8eF9gH0iJ2kL4mN6oP8qR
Key 2 (Doctor): mP5qR7sT1vW3yZ4aB6cD8eF9gH0iJ2kL4mN6oP8qRkJ8HfX2N9
Key 3 (Friend): T1vW3yZ4aB6cD8eF9gH0iJ2kL4mN6oP8qRkJ8HfX2N9mP5qR7s
Key 4 (App): 4aB6cD8eF9gH0iJ2kL4mN6oP8qRkJ8HfX2N9mP5qR7sT1vW3yZ
```

### Option 3: User-Friendly Setup (Advanced)

Create a simple setup page for users:

```python
# app/api/setup.py
from fastapi import APIRouter, HTTPException
from app.core.config import settings
import secrets

router = APIRouter()

@router.post("/generate-key")
async def generate_api_key(
    admin_key: str,
    description: str = "New API key"
):
    """Generate a new API key (admin only)."""
    if admin_key != settings.admin_key:
        raise HTTPException(401, "Invalid admin key")
    
    new_key = secrets.token_urlsafe(32)
    # In a real app, you'd save this to a database
    return {
        "api_key": new_key,
        "description": description,
        "created_at": datetime.now().isoformat()
    }
```

## Making It User-Friendly Like Nightscout

### 1. Create a Simple Setup Guide

```markdown
# Using My CGM API

## Quick Start
1. API URL: https://your-api.railway.app
2. Your API Key: [your-personal-key-here]
3. Test it: https://your-api.railway.app/docs

## For Developers
Use this in your app's Authorization header:
Bearer [your-personal-key-here]

## Examples
- Current glucose: GET /api/cgm/current
- 24h data: GET /api/cgm/data?hours=24
- Analysis: GET /api/cgm/analysis/24h
```

### 2. Create a Testing Page

```html
<!-- Create a simple test.html page -->
<!DOCTYPE html>
<html>
<head>
    <title>CGM API Test</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .result { background: #f0f0f0; padding: 20px; margin: 20px 0; }
        input { padding: 10px; margin: 10px 0; width: 400px; }
        button { padding: 10px 20px; background: #007cba; color: white; border: none; cursor: pointer; }
    </style>
</head>
<body>
    <h1>CGM API Test</h1>
    <p>Enter your API key to test the connection:</p>
    
    <input type="text" id="apiKey" placeholder="Enter your API key here">
    <button onclick="testAPI()">Test Connection</button>
    
    <div id="result" class="result" style="display: none;"></div>
    
    <script>
        async function testAPI() {
            const apiKey = document.getElementById('apiKey').value;
            const result = document.getElementById('result');
            
            if (!apiKey) {
                alert('Please enter your API key');
                return;
            }
            
            try {
                const response = await fetch('/api/cgm/current', {
                    headers: {
                        'Authorization': `Bearer ${apiKey}`
                    }
                });
                
                if (response.ok) {
                    const data = await response.json();
                    result.innerHTML = `
                        <h3>✅ Success!</h3>
                        <p>Current glucose: ${data.current_glucose} mg/dL</p>
                        <p>Direction: ${data.direction}</p>
                        <p>Updated: ${data.minutes_ago} minutes ago</p>
                    `;
                } else {
                    result.innerHTML = `<h3>❌ Error</h3><p>Status: ${response.status}</p>`;
                }
            } catch (error) {
                result.innerHTML = `<h3>❌ Error</h3><p>${error.message}</p>`;
            }
            
            result.style.display = 'block';
        }
    </script>
</body>
</html>
```

### 3. Documentation Site

Host a simple documentation site that explains:
- How to get an API key
- Example requests
- Code samples for different languages
- Troubleshooting guide

## Security Best Practices

### 1. Environment Variables Only
```bash
# ✅ Good - in .env file
API_KEY=your-secret-key-here

# ❌ Bad - in code
api_key = "your-secret-key-here"
```

### 2. Use HTTPS Only
All hosting platforms provide HTTPS automatically, but verify:
- Railway: Uses HTTPS by default
- Render: Uses HTTPS by default
- Fly.io: Uses HTTPS by default

### 3. Monitor Usage
Add logging to track API usage:

```python
# app/core/auth.py
import logging

logger = logging.getLogger(__name__)

def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify the API key and log usage."""
    if credentials.credentials != settings.api_key:
        logger.warning(f"Invalid API key attempt: {credentials.credentials[:10]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    logger.info(f"Valid API access with key: {credentials.credentials[:10]}...")
    return credentials.credentials
```

### 4. Rate Limiting (Optional)
For high-traffic scenarios:

```python
# Add to pyproject.toml dependencies
# slowapi = "^0.1.4"

# app/main.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add to endpoints
@limiter.limit("10/minute")
@router.get("/current")
async def get_current_glucose(request: Request, _: str = Depends(verify_api_key)):
    # ... rest of code
```

## Comparison with Nightscout

| Feature | Nightscout | Your Loopy API |
|---------|------------|----------------|
| **Authentication** | API_SECRET variable | API_KEY variable |
| **Setup Complexity** | Medium | Similar |
| **URL Format** | `site.com/api/v1/entries.json?token=secret` | `site.com/api/cgm/current` + Bearer token |
| **Data Format** | Nightscout JSON | Custom JSON (cleaner) |
| **Analysis** | Basic | Built-in comprehensive analysis |
| **Deployment** | Fly.io, Railway, Render | Same options |

## Migration from Open to Secured

If you already have an open API deployed:

1. **Update your code** with authentication
2. **Set the API_KEY environment variable**
3. **Test with the new authentication**
4. **Update any existing apps** that use your API
5. **Share new instructions** with users

The health endpoint will still work for monitoring, but all CGM data will require authentication.

## Troubleshooting

### "Invalid API key" Error
- Check the key matches exactly (no extra spaces)
- Verify the environment variable is set correctly
- Make sure you're using `Bearer` in the Authorization header

### "Authorization header missing"
- Ensure you're sending the `Authorization: Bearer your-key` header
- Check your HTTP client is configured correctly

### Users Can't Access
- Verify they're using the correct API URL
- Check their API key is valid
- Ensure they understand the Bearer token format

---

**This approach gives you Nightscout-level simplicity with better security for your medical data!**