# API Beginner's Guide: Understanding and Using Loopy API

## What is an API? (Simple Explanation)

Think of an API (Application Programming Interface) as a **waiter in a restaurant**:

1. **You** (a website/app) want some data
2. **The waiter** (the API) takes your request
3. **The kitchen** (your database) prepares the data
4. **The waiter** brings back the data in a nice format

```
Your Web App → API Request → Loopy API → MongoDB → Response → Your Web App
```

## How Does Loopy API Work?

### The Flow
```
CGM Device → Nightscout/xDrip → MongoDB → Loopy API → Your Website/App
```

### What Each Part Does:

1. **CGM Device** (Dexcom, Libre, etc.) - Measures your blood sugar
2. **Nightscout/xDrip** - Collects and stores the data in MongoDB
3. **MongoDB** - Database that holds all your glucose readings
4. **Loopy API** - Your new service that fetches and organizes the data
5. **Your Website/App** - Uses the organized data to show charts, alerts, etc.

## Real-World Example

Let's say you want to build a simple website that shows your current glucose:

### Step 1: Your Website Makes a Request
```javascript
// Your website's JavaScript code
fetch('https://your-api.railway.app/api/cgm/current')
```

### Step 2: Loopy API Processes the Request
- API receives the request
- Connects to your MongoDB database
- Finds your latest glucose reading
- Packages it in a clean format

### Step 3: API Sends Back Data
```json
{
  "current_glucose": 142,
  "direction": "Flat",
  "timestamp": "2025-01-16T10:30:00.000Z",
  "minutes_ago": 3.2
}
```

### Step 4: Your Website Uses the Data
```javascript
// Your website displays: "Current: 142 mg/dL (Flat)"
document.getElementById('glucose').textContent = data.current_glucose + ' mg/dL';
```

## Setting Up for Online Hosting

### Phase 1: Prepare Your Code

1. **Make sure your code is ready:**
```bash
# Test locally first
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
# Visit http://localhost:8000/docs to see it working
```

2. **Commit your code:**
```bash
git add .
git commit -m "Ready for deployment"
```

### Phase 2: Upload to GitHub

1. **Create a GitHub repository:**
   - Go to github.com
   - Click "New Repository"
   - Name it "loopy-api"
   - Make it public (so hosting services can access it)

2. **Push your code:**
```bash
git remote add origin https://github.com/yourusername/loopy-api.git
git push -u origin main
```

### Phase 3: Deploy to the Cloud

#### Option 1: Railway (Recommended - Easiest)

**Why Railway?**
- Free tier available
- Auto-deploys from GitHub
- Easy environment variable setup
- Gets you a URL like `https://loopy-api-production.up.railway.app`

**Steps:**
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your `loopy-api` repository
5. Railway automatically detects it's a Python project
6. Set environment variables:
   - `MONGODB_USERNAME` = your MongoDB username
   - `MONGODB_PW` = your MongoDB password
   - `MONGODB_URI` = your MongoDB connection string
   - `MONGODB_DATABASE` = myCGMitc
7. Click "Deploy"
8. Wait 2-3 minutes - you'll get a live URL!

#### Option 2: Render (Also Free)

**Steps:**
1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Click "New" → "Web Service"
4. Connect your GitHub repo
5. Settings:
   - **Build Command**: `uv sync`
   - **Start Command**: `uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Add environment variables (same as Railway)
7. Deploy

#### Option 3: Fly.io (More Advanced)

**Steps:**
1. Install Fly CLI: `curl -L https://fly.io/install.sh | sh`
2. Login: `fly auth login`
3. In your project: `fly launch`
4. Set secrets: `fly secrets set MONGODB_USERNAME=your_username`
5. Deploy: `fly deploy`

## How Other Apps Connect to Your API

### Web Applications (React, Vue, etc.)
```javascript
// Get current glucose
const response = await fetch('https://your-api.railway.app/api/cgm/current');
const data = await response.json();
console.log(`Current glucose: ${data.current_glucose} mg/dL`);

// Get 24-hour data for a chart
const chartData = await fetch('https://your-api.railway.app/api/cgm/data?hours=24');
const readings = await chartData.json();
// Use readings.data to build a glucose chart
```

### Mobile Apps
```swift
// iOS Swift example
let url = URL(string: "https://your-api.railway.app/api/cgm/current")!
let task = URLSession.shared.dataTask(with: url) { data, response, error in
    // Process the glucose data
}
task.resume()
```

### Data Analysis (Python)
```python
import requests
import pandas as pd

# Get data for analysis
response = requests.get('https://your-api.railway.app/api/cgm/data?hours=168')  # 1 week
data = response.json()

# Convert to DataFrame for analysis
df = pd.DataFrame(data['data'])
print(f"Average glucose this week: {df['sgv'].mean():.1f} mg/dL")
```

### Smart Home Integration
```python
# Home Assistant automation
# When glucose goes above 200, turn on red light
if glucose_reading > 200:
    turn_on_red_light()
```

## Security and Access

### Why Secure Your API?

Your CGM data is **medical information** that should be private. Without authentication, anyone who discovers your API URL can access your glucose readings, patterns, and health data.

### Authentication Options

#### Option 1: Keep it Simple (Current)
- Anyone can access your glucose data
- Fine for personal testing
- Easy to use from any app
- **Not recommended for production**

#### Option 2: API Key Authentication (Recommended)
- Simple password-like key for your API
- Similar to Nightscout's API_SECRET
- Easy to implement and use
- Can revoke access by changing the key

#### Option 3: Multiple API Keys (Advanced)
- Different keys for different users/apps
- Can revoke individual access
- Better for sharing with multiple people
- More management overhead

### Implementing API Key Authentication

#### Step 1: Add Authentication Code

Create authentication file:
```python
# app/core/auth.py
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings

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
```

#### Step 2: Update Configuration

Add to your `app/core/config.py`:
```python
# Add to your Settings class
api_key: str = secrets.token_urlsafe(32)  # Generate random key if not provided
```

#### Step 3: Protect Your Endpoints

Update your CGM endpoints:
```python
# app/api/cgm.py
from app.core.auth import verify_api_key

@router.get("/current")
async def get_current_glucose(
    _: str = Depends(verify_api_key)  # Add this line
) -> Dict[str, Any]:
    # ... rest of your code
```

#### Step 4: Set Environment Variables

In your hosting platform (Railway/Render/Fly.io):
```bash
# Generate a secure key
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Set in your hosting platform
API_KEY=your-generated-key-here
```

### Using Your Secured API

#### With curl:
```bash
# Before (unsecured)
curl https://your-api.railway.app/api/cgm/current

# After (secured)
curl -H "Authorization: Bearer your-api-key-here" https://your-api.railway.app/api/cgm/current
```

#### With JavaScript:
```javascript
const API_KEY = 'your-api-key-here';

const response = await fetch('https://your-api.railway.app/api/cgm/current', {
    headers: {
        'Authorization': `Bearer ${API_KEY}`
    }
});
```

#### With Python:
```python
import requests

headers = {'Authorization': 'Bearer your-api-key-here'}
response = requests.get('https://your-api.railway.app/api/cgm/current', headers=headers)
```

### Sharing Your Secured API

#### For Family/Friends:
1. Give them your API URL: `https://your-api.railway.app`
2. Give them your API key: `your-api-key-here`
3. Show them how to use it with the Authorization header

#### For Multiple Users:
Set up multiple keys:
```bash
# In your hosting platform
API_KEYS=key1-for-family,key2-for-doctor,key3-for-app
```

#### User-Friendly Setup:
Create a simple instruction sheet:
```markdown
# Using My CGM API

## Quick Start
1. API URL: https://your-api.railway.app
2. Your API Key: [personal-key-here]
3. Test it: Add "Authorization: Bearer [your-key]" header

## Example
curl -H "Authorization: Bearer [your-key]" https://your-api.railway.app/api/cgm/current
```

### Security Best Practices

1. **Use Environment Variables Only**
   - Never put API keys in your code
   - Set them in your hosting platform

2. **Generate Strong Keys**
   ```bash
   # Generate a secure 32-character key
   python3 -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

3. **Monitor Usage**
   - Check your hosting platform logs
   - Watch for unusual access patterns

4. **Rotate Keys Regularly**
   - Change your API key periodically
   - Update all apps that use it

5. **Use HTTPS Only**
   - All hosting platforms provide this automatically
   - Never use HTTP for medical data

### Migration from Open to Secured

If you already have an open API:
1. Add authentication code to your project
2. Set the API_KEY environment variable
3. Test with the new authentication
4. Update any existing apps
5. Share new instructions with users

The health endpoint (`/api/health`) stays public for monitoring.

### Comparison with Nightscout

| Feature | Nightscout | Your Loopy API |
|---------|------------|----------------|
| **Authentication** | API_SECRET variable | API_KEY variable |
| **Setup Complexity** | Medium | Similar |
| **URL Format** | `site.com/api/v1/entries.json?token=secret` | `site.com/api/cgm/current` + Bearer token |
| **Security** | Good | Same level |
| **Ease of Use** | Easy | Easy |

This gives you **Nightscout-level simplicity** with **better security** for your medical data!

## Testing Your Deployed API

Once deployed, test all endpoints:

### For Unsecured API:
```bash
# Replace with your actual URL
API_URL="https://your-api.railway.app"

# Test health (always works)
curl $API_URL/api/health

# Test current glucose
curl $API_URL/api/cgm/current

# Test data endpoint
curl "$API_URL/api/cgm/data?hours=24"
```

### For Secured API:
```bash
# Replace with your actual URL and API key
API_URL="https://your-api.railway.app"
API_KEY="your-api-key-here"

# Test health (no auth needed)
curl $API_URL/api/health

# Test current glucose (auth required)
curl -H "Authorization: Bearer $API_KEY" $API_URL/api/cgm/current

# Test data endpoint (auth required)
curl -H "Authorization: Bearer $API_KEY" "$API_URL/api/cgm/data?hours=24"

# Test analysis endpoint (auth required)
curl -H "Authorization: Bearer $API_KEY" $API_URL/api/cgm/analysis/24h
```

## Common Use Cases

### 1. Personal Dashboard Website
- Show current glucose, trends, and daily averages
- Display time-in-range charts
- Set up alerts for high/low glucose

### 2. Mobile App Integration
- Native iOS/Android apps
- Widget for phone home screen
- Push notifications for glucose alerts

### 3. Data Analysis
- Weekly/monthly reports
- A1C estimation
- Pattern recognition (meal impacts, exercise effects)

### 4. Smart Home Integration
- Philips Hue lights change color based on glucose
- Alexa announces glucose readings
- Automatic logging to health apps

### 5. Sharing with Healthcare Team
- Give your doctor access to real-time data
- Generate reports for appointments
- Family members can check your glucose

## Troubleshooting Common Issues

### "Internal Server Error"
- Check environment variables are set correctly
- Verify MongoDB connection string
- Check server logs in hosting platform

### "No recent data available"
- Verify your CGM is uploading to MongoDB
- Check MongoDB database name matches
- Ensure loopy-basic package can connect

### "CORS Error" (from web browser)
- Add your website domain to CORS_ORIGINS
- Update environment variable and redeploy

## Next Steps

1. **Deploy your API** using Railway or Render
2. **Test all endpoints** with your live URL
3. **Build a simple web page** that displays your glucose
4. **Share the API URL** with apps/services you want to integrate
5. **Consider adding authentication** if needed
6. **Monitor usage** and performance

## Cost Considerations

### Free Tier Limits
- **Railway**: 500 hours/month free, $5/month after
- **Render**: 750 hours/month free, then paid plans
- **Fly.io**: Generous free tier, pay for usage

### Typical Costs
- **Small personal use**: $0-5/month
- **Multiple apps accessing**: $5-10/month
- **High traffic**: $10-20/month

Most personal CGM APIs stay within free tiers!

## Example Integration Projects

### Simple Glucose Display Website

#### For Unsecured API:
```html
<!DOCTYPE html>
<html>
<head>
    <title>My Glucose</title>
</head>
<body>
    <h1>Current Glucose: <span id="glucose">Loading...</span></h1>
    <p>Direction: <span id="direction">Loading...</span></p>
    <p>Last updated: <span id="time">Loading...</span></p>

    <script>
        async function updateGlucose() {
            const response = await fetch('https://your-api.railway.app/api/cgm/current');
            const data = await response.json();
            
            document.getElementById('glucose').textContent = data.current_glucose + ' mg/dL';
            document.getElementById('direction').textContent = data.direction;
            document.getElementById('time').textContent = data.minutes_ago + ' minutes ago';
        }
        
        updateGlucose();
        setInterval(updateGlucose, 60000); // Update every minute
    </script>
</body>
</html>
```

#### For Secured API:
```html
<!DOCTYPE html>
<html>
<head>
    <title>My Glucose</title>
</head>
<body>
    <h1>Current Glucose: <span id="glucose">Loading...</span></h1>
    <p>Direction: <span id="direction">Loading...</span></p>
    <p>Last updated: <span id="time">Loading...</span></p>

    <script>
        const API_KEY = 'your-api-key-here';  // Replace with your actual API key
        
        async function updateGlucose() {
            const response = await fetch('https://your-api.railway.app/api/cgm/current', {
                headers: {
                    'Authorization': `Bearer ${API_KEY}`
                }
            });
            
            if (!response.ok) {
                document.getElementById('glucose').textContent = 'Error - Check API key';
                return;
            }
            
            const data = await response.json();
            
            document.getElementById('glucose').textContent = data.current_glucose + ' mg/dL';
            document.getElementById('direction').textContent = data.direction;
            document.getElementById('time').textContent = data.minutes_ago + ' minutes ago';
        }
        
        updateGlucose();
        setInterval(updateGlucose, 60000); // Update every minute
    </script>
</body>
</html>
```

### Python Data Analysis Script

#### For Unsecured API:
```python
import requests
import matplotlib.pyplot as plt
from datetime import datetime

# Get 24 hours of data
response = requests.get('https://your-api.railway.app/api/cgm/data?hours=24')
data = response.json()

# Extract glucose values and times
glucose_values = [reading['sgv'] for reading in data['data']]
times = [datetime.fromisoformat(reading['datetime'].replace('Z', '+00:00')) for reading in data['data']]

# Create a simple plot
plt.figure(figsize=(12, 6))
plt.plot(times, glucose_values, 'b-', linewidth=2)
plt.axhline(y=70, color='r', linestyle='--', label='Low (70)')
plt.axhline(y=180, color='r', linestyle='--', label='High (180)')
plt.title('24-Hour Glucose Trend')
plt.xlabel('Time')
plt.ylabel('Glucose (mg/dL)')
plt.legend()
plt.grid(True, alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

print(f"Average glucose: {sum(glucose_values)/len(glucose_values):.1f} mg/dL")
```

#### For Secured API:
```python
import requests
import matplotlib.pyplot as plt
from datetime import datetime

# Set up authentication
API_KEY = 'your-api-key-here'  # Replace with your actual API key
headers = {'Authorization': f'Bearer {API_KEY}'}

# Get 24 hours of data
response = requests.get('https://your-api.railway.app/api/cgm/data?hours=24', headers=headers)

if response.status_code != 200:
    print(f"Error: {response.status_code} - Check your API key")
    exit()

data = response.json()

# Extract glucose values and times
glucose_values = [reading['sgv'] for reading in data['data']]
times = [datetime.fromisoformat(reading['datetime'].replace('Z', '+00:00')) for reading in data['data']]

# Create a simple plot
plt.figure(figsize=(12, 6))
plt.plot(times, glucose_values, 'b-', linewidth=2)
plt.axhline(y=70, color='r', linestyle='--', label='Low (70)')
plt.axhline(y=180, color='r', linestyle='--', label='High (180)')
plt.title('24-Hour Glucose Trend')
plt.xlabel('Time')
plt.ylabel('Glucose (mg/dL)')
plt.legend()
plt.grid(True, alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

print(f"Average glucose: {sum(glucose_values)/len(glucose_values):.1f} mg/dL")
```

---

**Remember**: Your API is now a bridge between your CGM data and any application you want to build. The possibilities are endless!