# 🚀 Naukri.com Job Scraper for Apify

[![Apify Actor](https://img.shields.io/badge/Apify-Actor-00D4AA?style=flat&logo=apify)](https://apify.com)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Professional job scraper for Naukri.com** - Extract comprehensive job listings with advanced browser automation and residential proxies. Perfect for AI agents, ChatGPT plugins, Claude integrations, and MCP-powered automation workflows! 🤖

## 🎯 Features

✨ **Comprehensive Data Extraction**
- Job ID, title, company name
- Salary ranges and compensation
- Experience requirements (min/max years)
- Location and workplace details
- Skills and technologies required
- Full job descriptions
- Direct job URLs

🔒 **Anti-Bot Protection**
- Camoufox browser automation with realistic fingerprinting
- Residential proxy support via Apify
- Human-like behavior simulation
- GeoIP matching for proxy authenticity

🛡️ **Production-Ready**
- Robust error handling with retries
- Graceful degradation (null for missing fields)
- Real-time data pushing to Apify dataset
- Comprehensive logging and monitoring

🤖 **AI-Friendly**
- Built for Claude, ChatGPT, and MCP agents
- Clean, structured JSON output
- Timestamp tracking for data freshness
- Easy integration with AI workflows

## 📊 Output Schema

Each job listing includes the following fields:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `jobId` | string | Unique job identifier | `"290524001234"` |
| `title` | string | Job title | `"Senior Software Engineer"` |
| `companyName` | string | Company name | `"Tech Corp India"` |
| `salary` | string\|null | Salary information | `"15-25 Lacs P.A."` |
| `experienceMin` | integer\|null | Minimum experience (years) | `3` |
| `experienceMax` | integer\|null | Maximum experience (years) | `5` |
| `location` | string\|null | Job location | `"Bangalore, Pune"` |
| `skills` | array\|null | Required skills | `["Python", "AWS", "Docker"]` |
| `jobDescription` | string\|null | Job description | `"We are looking for..."` |
| `jobUrl` | string\|null | Direct link to job posting | `"https://www.naukri.com/..."` |
| `scrapedAt` | string | Scraping timestamp (ISO 8601) | `"2024-08-21T10:30:00.000Z"` |

## 🚀 Quick Start

### Running on Apify Platform

1. **Create a new Actor** from this repository
2. **Configure input parameters:**
   - `searchQuery`: Job title or keywords (e.g., "software engineer")
   - `location`: City name (e.g., "bangalore") or leave empty for all locations
   - `maxResults`: Number of jobs to scrape (1-500)

3. **Run the Actor** and access results from the dataset

### Input Example

```json
{
  "searchQuery": "data scientist",
  "location": "bangalore",
  "maxResults": 100
}
```

### Using Prefills

We provide convenient prefills for common searches:

- 🔧 **Software Engineer - Bangalore**
- 📊 **Data Scientist - All India**
- 📱 **Product Manager - Mumbai**
- ⚙️ **DevOps Engineer - Pune**
- 💻 **Full Stack Developer - Hyderabad**

## 🤖 AI Integration Examples

### Claude Desktop (MCP)

Use this actor directly from Claude Desktop via the Apify MCP server:

```json
{
  "apify": {
    "actorId": "your-actor-id",
    "input": {
      "searchQuery": "machine learning engineer",
      "location": "bangalore",
      "maxResults": 50
    }
  }
}
```

### ChatGPT Actions

Integrate with ChatGPT using Apify's API:

```yaml
openapi: 3.0.0
paths:
  /v2/acts/{actorId}/runs:
    post:
      summary: Scrape Naukri.com jobs
      parameters:
        - name: actorId
          in: path
          required: true
          schema:
            type: string
      requestBody:
        content:
          application/json:
            schema:
              properties:
                searchQuery:
                  type: string
                location:
                  type: string
                maxResults:
                  type: integer
```

### Python Integration

```python
from apify_client import ApifyClient

client = ApifyClient('your-apify-token')

# Start the actor
run = client.actor('your-actor-id').call(run_input={
    'searchQuery': 'python developer',
    'location': 'mumbai',
    'maxResults': 100
})

# Fetch results
dataset_items = client.dataset(run['defaultDatasetId']).list_items().items

for job in dataset_items:
    print(f"{job['title']} at {job['companyName']}")
    print(f"Location: {job['location']}")
    print(f"Salary: {job['salary']}")
    print(f"Skills: {', '.join(job['skills'] or [])}")
    print(f"URL: {job['jobUrl']}\n")
```

### Node.js Integration

```javascript
import { ApifyClient } from 'apify-client';

const client = new ApifyClient({ token: 'your-apify-token' });

// Start the actor
const run = await client.actor('your-actor-id').call({
    searchQuery: 'react developer',
    location: 'bangalore',
    maxResults: 50
});

// Fetch results
const { items } = await client.dataset(run.defaultDatasetId).listItems();

items.forEach(job => {
    console.log(`${job.title} at ${job.companyName}`);
    console.log(`Location: ${job.location}`);
    console.log(`Skills: ${job.skills?.join(', ')}`);
});
```

## 🔧 Local Development

### Prerequisites

- Python 3.11+
- Docker (for containerized testing)

### Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd naukri-job-scraper-mcp

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export APIFY_TOKEN=your_apify_token

# Run locally
python -m src
```

### Testing with Apify CLI

```bash
# Install Apify CLI
npm install -g apify-cli

# Login to Apify
apify login

# Run the actor locally
apify run
```

## 📋 Technical Details

### Technology Stack

- **Language**: Python 3.11
- **Browser Automation**: Camoufox (Firefox-based stealth browser)
- **HTML Parsing**: BeautifulSoup4 + lxml
- **Platform**: Apify Actor Framework
- **Proxy**: Apify Residential Proxies

### Architecture

```
┌─────────────────┐
│  Apify Platform │
└────────┬────────┘
         │
    ┌────▼─────┐
    │   Actor  │
    └────┬─────┘
         │
    ┌────▼────────┐
    │  Camoufox   │ ◄──── Residential Proxy
    │  Browser    │
    └────┬────────┘
         │
    ┌────▼──────────┐
    │  Naukri.com   │
    │  (Next.js SPA)│
    └────┬──────────┘
         │
    ┌────▼─────────┐
    │  BeautifulSoup│
    │  Parser       │
    └────┬─────────┘
         │
    ┌────▼─────────┐
    │ Apify Dataset│
    └──────────────┘
```

### Error Handling

- **Retry Logic**: 3 attempts with exponential backoff
- **Graceful Failures**: Returns `null` for missing fields instead of crashing
- **Proxy Fallback**: Continues without proxy if residential proxy fails
- **Logging**: Comprehensive error logging for debugging

## 🌟 Use Cases

- 🎯 **Job Market Research**: Analyze salary trends and skill demands
- 🤖 **AI-Powered Job Matching**: Feed data to LLMs for personalized recommendations
- 📈 **Recruitment Analytics**: Track hiring trends and company activity
- 🔔 **Job Alerts**: Build automated notification systems
- 💼 **Career Planning**: Understand experience requirements across industries

## 🛠️ Customization

### Modify Search Parameters

Edit `src/main.py` to add custom filters:

```python
# Add custom filters
experience_filter = actor_input.get('experienceRange', '')
salary_filter = actor_input.get('salaryMin', '')
```

### Extend Data Extraction

Edit `src/parser.py` to extract additional fields:

```python
# Add new field extraction
posted_date = _clean_text(job_card.select_one('.posted-date').get_text())
job_data['postedDate'] = posted_date
```

## 📝 License

MIT License - feel free to use this actor for commercial or personal projects.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 💬 Support

- 📧 **Issues**: Open an issue on GitHub
- 💡 **Feature Requests**: Submit via GitHub Issues
- 📚 **Documentation**: [Apify Documentation](https://docs.apify.com)

## 🎉 Built With AI

This actor was built with assistance from Claude AI and is optimized for AI agent workflows, MCP integrations, and ChatGPT automation. Perfect for building intelligent job search assistants! 🚀

---

**Made with ❤️ for the AI automation community**
