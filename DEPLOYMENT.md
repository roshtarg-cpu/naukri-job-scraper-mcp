# 🚀 Deployment Guide - Naukri.com Job Scraper

## Quick Deploy to Apify Platform

### Option 1: Deploy via Apify Console

1. **Create a new Actor**:
   ```bash
   # Install Apify CLI (if not already installed)
   npm install -g apify-cli
   
   # Login to Apify
   apify login
   
   # Navigate to the actor directory
   cd ~/actors/naukri-job-scraper-mcp
   
   # Initialize (if needed) and push to Apify
   apify push
   ```

2. **Or upload manually**:
   - Go to https://console.apify.com/actors
   - Click "Create new" → "From scratch"
   - Upload all files from `~/actors/naukri-job-scraper-mcp/`
   - Click "Build" to create the Docker image

### Option 2: Connect GitHub Repository

1. **Push to GitHub**:
   ```bash
   cd ~/actors/naukri-job-scraper-mcp
   git init
   git add .
   git commit -m "Initial commit: Naukri.com Job Scraper"
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **Connect to Apify**:
   - Go to Apify Console → Create Actor
   - Choose "From GitHub repository"
   - Enter your repository URL
   - Apify will auto-build on each push

## 🧪 Local Testing

### Test with Apify CLI

```bash
cd ~/actors/naukri-job-scraper-mcp

# Create a test input file
cat > test_input.json << 'EOF'
{
  "searchQuery": "python developer",
  "location": "bangalore",
  "maxResults": 10
}
EOF

# Run the actor locally
apify run --input-file test_input.json

# Results will be in ./apify_storage/datasets/default/
```

### Test with Docker

```bash
cd ~/actors/naukri-job-scraper-mcp

# Build the Docker image
docker build -t naukri-scraper .

# Run with environment variables
docker run -e APIFY_TOKEN=your_token \
           -e APIFY_INPUT='{"searchQuery":"software engineer","location":"mumbai","maxResults":20}' \
           naukri-scraper
```

### Test Python Code Directly

```bash
cd ~/actors/naukri-job-scraper-mcp

# Install dependencies in a virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set environment variables
export APIFY_TOKEN=your_apify_token
export APIFY_INPUT='{"searchQuery":"data scientist","location":"pune","maxResults":15}'

# Run the actor
python -m src
```

## 🔑 Required Configuration

### Apify Token

Get your token from: https://console.apify.com/account/integrations

```bash
export APIFY_TOKEN=apify_api_xxxxxxxxxxxxxxxxxxxxxxxx
```

### Residential Proxy

The actor automatically uses Apify's residential proxies. Make sure you have:
- Active Apify subscription with residential proxy access
- Or set `useApifyProxy: false` in main.py for testing without proxies

## 📊 Monitor Runs

### Via Apify Console

1. Go to https://console.apify.com/actors
2. Click on your actor
3. View "Runs" tab for:
   - Live logs
   - Dataset preview
   - Run statistics
   - Cost breakdown

### Via Apify API

```bash
# Get run details
curl -X GET "https://api.apify.com/v2/actor-runs/<run_id>" \
     -H "Authorization: Bearer <your_token>"

# Get dataset items
curl -X GET "https://api.apify.com/v2/datasets/<dataset_id>/items" \
     -H "Authorization: Bearer <your_token>"
```

## 🐛 Troubleshooting

### Issue: Actor fails to build

**Solution**: Check Dockerfile dependencies
```bash
# Test Docker build locally
docker build -t test-naukri .
```

### Issue: No jobs found

**Solution**: Check search query and location
- Verify Naukri.com has jobs for that query
- Try broader search terms
- Check if location is spelled correctly

### Issue: Proxy errors

**Solution**: 
```python
# Temporarily disable proxy for testing
proxy_url = None  # in src/main.py
```

### Issue: Parsing errors

**Solution**: Naukri.com might have changed their HTML structure
- Inspect the page HTML
- Update selectors in `src/parser.py`
- Check browser console for dynamic loading

## 📈 Scaling

### Increase Performance

1. **Parallel Requests**:
   ```python
   # Modify main.py to use concurrent scraping
   tasks = [fetch_jobs_page(url, proxy_url) for url in urls]
   results = await asyncio.gather(*tasks)
   ```

2. **Multiple Locations**:
   ```json
   {
     "searchQuery": "software engineer",
     "locations": ["bangalore", "mumbai", "pune", "delhi"],
     "maxResults": 200
   }
   ```

3. **Scheduled Runs**:
   - Use Apify Scheduler
   - Set up cron-like schedules
   - Get fresh job listings daily

## 🤖 AI Integration

### Use with Claude Desktop (MCP)

Install the Apify MCP server and call the actor:

```json
{
  "apify": {
    "actorId": "your-username/naukri-job-scraper-mcp",
    "input": {
      "searchQuery": "machine learning engineer",
      "location": "bangalore",
      "maxResults": 50
    }
  }
}
```

### Use with ChatGPT

Create a custom GPT action pointing to Apify API endpoint.

### Use with Python Script

```python
from apify_client import ApifyClient

client = ApifyClient('your_token')
run = client.actor('your-username/naukri-job-scraper-mcp').call(
    run_input={
        'searchQuery': 'react developer',
        'location': 'bangalore',
        'maxResults': 100
    }
)

# Get results
items = client.dataset(run['defaultDatasetId']).list_items().items
print(f"Found {len(items)} jobs")
```

## 💰 Cost Estimation

Approximate costs on Apify:
- **Compute**: ~$0.02 per 100 jobs scraped
- **Residential Proxy**: ~$0.10 per 100 requests
- **Storage**: Minimal (datasets are free up to 100GB)

**Total**: ~$0.12 per 100 jobs with residential proxies

## ✅ Pre-deployment Checklist

- [ ] All files present (10 files)
- [ ] Python syntax validated
- [ ] JSON schemas validated
- [ ] Dockerfile builds successfully
- [ ] Local test run completes
- [ ] Apify token configured
- [ ] README.md is complete
- [ ] .gitignore includes sensitive files
- [ ] Actor name is unique on Apify
- [ ] Residential proxy access enabled

## 🎉 Ready to Deploy!

Your Naukri.com Job Scraper is production-ready and can be deployed immediately to Apify platform!
