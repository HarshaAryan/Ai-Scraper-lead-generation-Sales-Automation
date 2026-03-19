```
# Advanced AI Web Scraper - Local Architecture

## Architecture Overview

This is an **intelligent, locally-hosted web scraper** that searches the internet, scrapes multiple websites, and uses AI to extract structured data based on natural language queries. Built for power and flexibility while keeping setup simple.

### Core Design Principles
- **Local-First**: All data stored locally, no database setup required
- **AI-Powered**: Uses LLMs at every step - search understanding, site selection, data extraction
- **Multi-Source**: Searches and scrapes across the entire internet, not just single sites
- **Intelligent Processing**: AI decides what to scrape and how to extract data
- **Single-Machine**: Runs on your laptop/desktop with minimal setup

## System Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                       Web Browser (UI)                               │
│                React Frontend (localhost:3000)                       │
└────────────────────────────┬─────────────────────────────────────────┘
                             │ HTTP/SSE (Server-Sent Events)
┌────────────────────────────▼─────────────────────────────────────────┐
│                        FastAPI Backend (localhost:8000)              │
│                                                                       │
│  ┌──────────────┐         ┌─────────────────────────────────┐       │
│  │   Job API    │────────▶│   AI Orchestrator               │       │
│  │   Routes     │         │   (Coordinates entire process)  │       │
│  └──────────────┘         └──────────────┬──────────────────┘       │
│                                          │                           │
│                    ┌─────────────────────┼──────────────────┐       │
│                    │                     │                  │       │
│           ┌────────▼────────┐   ┌───────▼────────┐  ┌──────▼─────┐ │
│           │  AI Search       │   │  Smart Scraper │  │ AI Data    │ │
│           │  Engine          │   │  Engine        │  │ Extractor  │ │
│           │                  │   │                │  │            │ │
│           │ • Query AI       │   │ • Playwright   │  │ • Schema   │ │
│           │ • Find URLs      │   │ • BeautifulSoup│  │   Gen      │ │
│           │ • Rank sites     │   │ • Anti-block   │  │ • Extract  │ │
│           └────────┬─────────┘   └───────┬────────┘  │ • Validate │ │
│                  

| Component | Technology | Why This Choice |
| :--- | :--- | :--- |
| **Backend** | **FastAPI** | Async support, WebSocket/SSE for real-time updates, perfect for I/O-bound tasks |
| **Data Storage** | **JSON Files** | No database setup, human-readable, easy to backup and inspect |
| **Web Search** | **SerpAPI / Google Custom Search** | Find websites across the internet based on natural language queries |
| **Scraping** | **Playwright + BeautifulSoup** | Playwright for JS-heavy sites, BeautifulSoup for static HTML - best of both worlds |
| **AI Processing** | **OpenAI GPT-4 / Anthropic Claude** | Advanced reasoning for query understanding, site selection, and data extraction |
| **AI Framework** | **LangChain (Optional)** | Helps structure AI workflows and chains multiple AI operations |
| **Frontend** | **React + Vite** | Fast dev server, modern UI, real-time updates |
| **Styling** | **Tailwind CSS + shadcn/ui** | Beautiful components out of the box |
| *How AI Powers the Scraper (Multi-Stage AI Integration)

### 1. **AI Search Engine** - Understanding Intent
**What it does:** Converts natural language to search queries and finds relevant websites
```
User Input: "Find top-rated Italian restaurants in San Francisco with outdoor seating"

AI Processing:
1. Extracts key parameters: location, industry, specific attributes
2. Generates search queries: ["best Italian restaurants San Francisco outdoor seating", 
                              "Italian restaurants SF patio dining", ...]
3. Searches web using SerpAPI/Google
4. AI ranks and filters URLs by relevance
5. Returns top 20-50 URLs to scrape
```

### 2. **Smart Scraper** - Intelligent Content Extraction
**What it does:** Adapts scraping strategy per website
```
For each URL:
1. AI analyzes the URL and predicts content type (restaurant page, listing, review site)
2. Chooses scraping method (Playwright for JS-heavy, BeautifulSoup for static)
3. Identifies anti-bot measures and adjusts headers/delays
4. Extracts raw HTML and relevant sections
```

### 3. **AI Data Extractor** - Structured Data Extraction
**What it does:** Converts messy HTML into structured JSON
```
Input: Raw HTML + User's data requirements
AI Prompt: "Extract restaurant name, address, phone, rating, outdoor seating (yes/no)"

Output: 
{
  "name": "Sotto Mare",
  "address": "552 Green St, San Francisco, CA 94133",
  "phone": "(415) 398-3181",
  "rating": 4.5,
  "outdoor_seating": true
}      # FastAPI app entry
│   │   ├── models.py                  # Pydantic data models
│   │   ├── config.py                  # Configuration & API keys
│   │   │
│   │   ├── core/
│   │   │   ├── storage.py             # JSON file operations
│   │   │   └── logger.py              # Logging setup
│   │   │
│   │   ├── ai/
│   │   │   ├── llm_client.py          # OpenAI/Anthropic client
│   │   │   ├── prompts.py             # AI prompt templates
│   │   │   ├── search_engine.py       # AI-powered search
│   │   │   ├── data_extractor.py      # AI data extraction
│   │   │   └── validator.py           # AI validation & cleaning
│   │   │
│   │   ├── scraper/
│   │   │   ├── playwright_scraper.py  # JS-heavy sites
│   │   │   ├── beautifulsoup_scraper.py # Static sites
│   │   │   ├── anti_block.py          # Anti-blocking strategies
│   │   │   └── url_manager.py         # URL queue & deduplication
│   │   │
│   │   ├── services/
│   │   │   ├── orchestrator.py        # Main AI workflow
│   │   │   ├── search_service.py      # SerpAPI/Google integration
│   │   │   └── job_processor.py       # Background job handler
│   │   │
│   │   └── routers/
│   │       ├── jobs.py                # Job API endpoints
│   │       └── sse.py                 # Server-Sent Events
│   │
│   ├── data/
│   │   ├── jobs/                      # Job metadata & status
│   │   ├── rsearching|scraping|extracting|validating|completed|failed",
  "created_at": "2026-01-20T10:30:00",
  "query": "Find top-rated Italian restaurants in San Francisco with outdoor seating",
  "params": {
    "location": "San Francisco, CA",
    "industry": "restaurants",
    "filters": ["Italian", "outdoor seating", "highly rated"],
    "extraction_schema": {
      "name": "string",
      "address": "string",
      "phone": "string",
      "rating": "float",
      "outdoor_seating": "boolean",
      "price_range": "string"
    }
  },
  "progress": {
    "stage": "extracting",
    "urls_found": 45,
    "urls_scraped": 30,
    "data_extracted": 25,
    "validation_passed": 20,
    "percentage": 66.7
  },
  "ai_insights": {
    "search_queries_generated": 3,
    "total_api_calls": 35,
    "confidence_score": 0.87
  },
  "error": null
}
```

### Results Storage (`data/results/{job_id}.json`)
```json
{Example AI Workflow

```
User Query: "Find top-rated Italian restaurants in San Francisco with outdoor seating"

Step 1 - AI Search Engine:
├─ AI analyzes query → Extracts: location="SF", category="restaurants", 
│                       cuisine="Italian", feature="outdoor seating"
├─ Generates search queries:
│  • "best Italian restaurants San Francisco outdoor seating"
│  • "top rated Italian dining SF patio"
│  • "Italian restaurants North Beach outdoor tables"
├─ SerpAPI returns 150 URLs
└─ AI filters and ranks → Top 40 most relevant URLs

Step 2 - Smart Scraper:
├─ For each URL in parallel (async):
│  ├─ AI predicts site type (Yelp? Own site? Review site?)
│  ├─ Chooses Playwright (Yelp) or BeautifulSoup (static sites)
│  ├─ Scrapes with anti-blocking (random delays, rotating user agents)
│  └─ Saves raw HTML to data/raw/
└─ 35/40 URLs scraped successfully

Step 3 - AI Data Extractor:
├─ For each scraped page:
│  ├─ AI identifies relevant content sections
│  ├─ Extracts structured data via LLM:
│  │  Prompt: "From this HTML, extract: name, address, phone, rating, 
│  │           outdoor_seating (boolean). Return JSON."
│  └─ Validates against schema
└─ 30/35 pages extracted successfully

Step 4 - AI Validator:
├─ Deduplicates (same restaurant from multiple sources)
├─ Validates phone format, address completeness
├─ AI enriches missing data from context
├─ Assigns confidence scores
└─ Returns 20 high-quality results

Total Time: ~3-5 minutes
AI Cost: ~$0.30-0.50 (depending on model)
```

## API Keys Required

Create a `.env` file:
```bash
# AI Models (choose one or both)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Web Search (choose one)
SERPAPI_KEY=...                    # serpapi.com (free tier: 100 searches/month)
GOOGLE_SEARCH_API_KEY=...          # Google Custom Search
GOOGLE_SEARCH_ENGINE_ID=...

# Optional
PROXIES_ENABLED=false              # Set to true if using proxies
```

## Running Locally

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Create .env file with API keys
cp .env.example .env
# Edit .env and add your API keys

# Run
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev  # Runs on localhost:3000
```

### Usage
1. Open browser → `http://localhost:3000`
2. Enter natural language query: "Find top vegan cafes in Austin with wifi"
3. Watch real-time progress as AI searches, scrapes, and extracts
4. View structured results in table
5. Export to CSV/JSON

## Key Dependencies

**Backend:**
```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
playwright==1.41.0
beautifulsoup4==4.12.3
httpx==0.26.0
openai==1.10.0
anthropic==0.18.0
pydantic==2.6.0
python-dotenv==1.0.0
google-search-results==2.4.2  # SerpAPI
```

## Advanced Features

### 1. **Multi-Model AI Strategy**
- Use GPT-4 for complex reasoning (search query generation, validation)
- Use GPT-3.5-turbo for simple extraction (cost-effective)
- Fallback mechanism if one API is down

### 2. **Smart Caching**
- Cache search results for 24 hours
- Cache scraped HTML to avoid re-scraping
- LRU cache for repeated AI queries

### 3. **Adaptive Scraping**
- AI detects if page needs JavaScript rendering
- Automatically switches between Playwright and BeautifulSoup
- Learns from failed attempts

### 4. **Parallel Processing**
- Scrape multiple URLs concurrently (asyncio)
- Batch AI requests to reduce latency
- Thread pool for CPU-intensive parsing

### 5. **Anti-Blocking**
- Rotating user agents
- Random delays between requests
- Respect robots.txt
- Optional: residential proxies for production

## Future Enhancements

- **SQLite**: For better querying and job history
- **Vector DB**: For semantic search across results
- **Custom Models**: Fine-tuned extraction models
- **API Access**: RESTful API for programmatic access
- **Scheduled Jobs**: Periodic re-scraping
- **Data Visualization**: Charts and insights from result
    "ai_cost_estimate": "$0.45",
    "sources_scraped": 45
  }, delays)
- Raw HTML storage

### Phase 2: Advanced AI Extraction (2-3 Days)

**Day 4: AI Data Extractor**
- Schema generation from user prompts
- LLM-based data extraction pipeline
- Structured output validation (Pydantic)
- Error handling and retries

**Day 5: AI Orchestration**
- Multi-stage AI workflow
- Progress tracking and logging
- Parallel processing of multiple URLs
- Result aggregation

### Phase 3: Frontend & Polish (2-3 Days)

**Day 6: REST API & WebSockets**
- Job submission endpoint
- Real-time progress updates (SSE)
- Results retrieval
- Job history

**Day 7-8: Web Interface**
- React app with Vite
- Natural language query input
- Live progress dashboard
- Interactive results viewer with filtering
- Export to CSV/JSONh or manual input)
- Implement web scraper with BeautifulSoup/Requests
- Add error handling and retry logic

**Day 3: AI Integration**
- Integrate OpenAI API for content structuring
- Create prompt templates
- Implement data extraction and validation

### Phase 2: API & Frontend (2-3 Days)

**Day 4: REST API**
- Create job submission endpoint
- Build job status checking endpoint
- Add results retrieval endpoint
- Implement background task processing

**Day 5-6: Web Interface**
- React app setup with Vite
- Job submission form (location, industry, prompt)
- Job status dashboard
- Results viewer (table view, JSON export)

## Project Structure

```
ai-scraper/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry
│   │   ├── models.py            # Data models
│   │   ├── storage.py           # JSON file operations
│   │   ├── scraper.py           # Web scraping logic
│   │   ├── ai_processor.py      # OpenAI integration
│   │   └── routers/
│   │       └── jobs.py          # API endpoints
│   ├── data/
│   │   ├── jobs/                # Job metadata (JSON)
│   │   └── results/             # Scraped results (JSON)
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── JobForm.jsx
│   │   │   ├── JobStatus.jsx
│   │   │   └── ResultsViewer.jsx
│   │   └── api/
│   │       └── client.js
│   └── package.json
│
└── README.md
```

## Data Storage Format

### Jobs Storage (`data/jobs/{job_id}.json`)
```json
{
  "id": "uuid-here",
  "status": "pending|processing|completed|failed",
  "created_at": "2026-01-20T10:30:00",
  "params": {
    "location": "San Francisco",
    "industry": "restaurants",
    "prompt": "Extract name, address, phone, rating"
  },
  "progress": {
    "urls_found": 10,
    "urls_scraped": 5,
    "urls_processed": 3
  },
  "error": null
}
```

### Results Storage (`data/results/{job_id}.json`)
```json
{
  "job_id": "uuid-here",
  "data": [
    {
      "url": "https://example.com",
      "extracted": {
        "name": "Best Restaurant",
        "address": "123 Main St",
        "phone": "555-1234",
        "rating": 4.5
      }
    }
  ],
  "completed_at": "2026-01-20T11:00:00"
}
```

## Running Locally

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev  # Runs on localhost:3000
```

## Future Enhancements (Optional)

When you need more power, you can gradually add:
- **SQLite** → For better querying (still local, no server)
- **Playwright** → For JavaScript-heavy sites
- **Background Workers** → For parallel processing
- **Docker** → For easier deployment
- **Authentication** → If sharing with others
```

live
