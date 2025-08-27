# How to Use Your Docker-Deployed Multi-Agent Content Analytics Application

## 🎯 Understanding What You Have

Your Multi-Agent Content Analytics application is now running as a **web API** inside a Docker container. Think of it like a smart service that you can talk to through HTTP requests.

## 🌐 How Docker Applications Work

When you deploy on Docker:
1. **Your app runs inside a container** (like a mini computer)
2. **It exposes a web API on port 8000** 
3. **You interact with it through HTTP requests** (like visiting a website)
4. **It responds with JSON data** that contains the analysis results

## 🚀 Quick Start - Using Your Application

### Step 1: Make Sure It's Running
```bash
# Check if container is running
docker-compose ps

# You should see something like:
# multi-agent-content-analytics-api-1   Up 2 minutes (healthy)   0.0.0.0:8000->8000/tcp
```

### Step 2: Test Basic Connectivity
```bash
# Test if the API is responding
curl http://localhost:8000/

# Expected response:
# {"message":"Multi-Agent Content Analytics API","status":"running"}
```

## 📱 Ways to Use Your Application

### Method 1: Using curl (Command Line)

**Check API Health:**
```bash
curl http://localhost:8000/health
```

**See Available AI Agents:**
```bash
curl http://localhost:8000/agents
```

**Analyze Movie Script Content:**
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "content": "FADE IN: EXT. SPACESHIP - DAY. The massive starship hovers above Earth. Captain Sarah looks out the window at her home planet one last time before the journey to Mars begins.",
    "analysis_type": "detailed"
  }'
```

### Method 2: Using a Web Browser

**Simple GET Requests:**
- Open browser and go to: `http://localhost:8000/`
- Check health: `http://localhost:8000/health`
- View agents: `http://localhost:8000/agents`

### Method 3: Using Postman (Recommended for Complex Requests)

1. **Download Postman** (free API testing tool)
2. **Create a new request:**
   - Method: `POST`
   - URL: `http://localhost:8000/analyze`
   - Headers: `Content-Type: application/json`
   - Body (raw JSON):
   ```json
   {
     "content": "Your movie script or content here",
     "analysis_type": "detailed"
   }
   ```

### Method 4: Using Python Script

Create a simple Python script to interact with your API:

```python
import requests
import json

# API base URL
API_URL = "http://localhost:8000"

def analyze_content(content, analysis_type="basic"):
    """Send content to your API for analysis"""
    response = requests.post(
        f"{API_URL}/analyze",
        json={
            "content": content,
            "analysis_type": analysis_type
        }
    )
    return response.json()

# Example usage
if __name__ == "__main__":
    # Test the API
    script_content = """
    FADE IN:
    EXT. ALIEN PLANET - DAY
    
    The red desert stretches endlessly. Two astronauts in white suits 
    walk across the barren landscape, their breathing heavy through 
    the radio static.
    
    ASTRONAUT 1
    We're not alone here.
    
    A shadow moves behind a distant rock formation.
    """
    
    result = analyze_content(script_content, "detailed")
    print(json.dumps(result, indent=2))
```

## 🎬 Real-World Usage Examples

### Example 1: Analyzing a Movie Script
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "content": "INT. SPACESHIP BRIDGE - NIGHT. The crew discovers an alien signal. CAPTAIN: This changes everything. We are not alone in the universe.",
    "analysis_type": "detailed"
  }'
```

**What you get back:**
```json
{
  "content": "INT. SPACESHIP BRIDGE - NIGHT...",
  "analysis_type": "detailed",
  "results": {
    "word_count": 20,
    "character_count": 125,
    "sentiment": "positive",
    "keywords": ["content", "analysis"],
    "summary": "Analysis of detailed content with 20 words"
  }
}
```

### Example 2: Checking Available Agents
```bash
curl http://localhost:8000/agents
```

**Response:**
```json
{
  "agents": [
    {
      "name": "script_summarizer",
      "description": "Analyzes and summarizes movie scripts",
      "status": "available"
    },
    {
      "name": "genre_classifier", 
      "description": "Classifies content by genre",
      "status": "available"
    },
    {
      "name": "marketing_agent",
      "description": "Generates marketing recommendations", 
      "status": "available"
    }
  ]
}
```

## 🔧 Managing Your Docker Application

### Starting and Stopping
```bash
# Start the application
docker-compose up -d

# Stop the application  
docker-compose down

# Restart the application
docker-compose restart

# View logs in real-time
docker-compose logs -f api
```

### Checking Status
```bash
# See if container is running
docker-compose ps

# Check container health
curl http://localhost:8000/health

# View resource usage
docker stats multi-agent-content-analytics-api-1
```

## 💡 Integration Ideas

### 1. Build a Simple Web Interface
Create an HTML form that sends requests to your API:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Content Analytics</title>
</head>
<body>
    <h1>Movie Script Analyzer</h1>
    <textarea id="content" placeholder="Paste your script here..."></textarea>
    <button onclick="analyzeContent()">Analyze</button>
    <div id="results"></div>
    
    <script>
        async function analyzeContent() {
            const content = document.getElementById('content').value;
            const response = await fetch('http://localhost:8000/analyze', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({content, analysis_type: 'detailed'})
            });
            const result = await response.json();
            document.getElementById('results').innerHTML = 
                '<pre>' + JSON.stringify(result, null, 2) + '</pre>';
        }
    </script>
</body>
</html>
```

### 2. Connect to Other Applications
Your API can be integrated with:
- **Slack bots** (analyze scripts shared in channels)
- **Web applications** (content analysis features)
- **Mobile apps** (script analysis on-the-go)
- **Automated workflows** (batch processing scripts)

## 🌍 Accessing From Other Machines

If you want to use this from other computers on your network:

1. **Find your computer's IP address:**
   ```bash
   ipconfig getifaddr en0  # On Mac
   # or
   hostname -I  # On Linux
   ```

2. **Use that IP instead of localhost:**
   ```bash
   curl http://YOUR_IP_ADDRESS:8000/health
   ```

## 🔍 Troubleshooting

### Application Won't Start
```bash
# Check if port 8000 is already in use
lsof -i :8000

# View detailed logs
docker-compose logs api
```

### API Not Responding
```bash
# Test basic connectivity
curl -v http://localhost:8000/health

# Check container status
docker-compose ps
```

### Getting JSON Format Errors
Make sure your requests include the correct headers:
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"content": "your content", "analysis_type": "basic"}'
```

## 🎯 Summary

Your Docker-deployed application is a **RESTful API service** that:
- ✅ Runs on `http://localhost:8000`
- ✅ Accepts HTTP requests with movie script content
- ✅ Returns JSON analysis results
- ✅ Can be used by any programming language or tool that speaks HTTP
- ✅ Provides 4 main endpoints: `/`, `/health`, `/agents`, `/analyze`

**Think of it as your personal content analysis server that other applications can talk to!** 🚀
