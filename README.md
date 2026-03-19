# Super-Scraper 🚀

**An AI-powered lead generation platform that searches the internet, scrapes multiple websites, and extracts structured data based on natural language queries.**

Built with **LangGraph**, **Streamlit**, and advanced AI agents.

---

## Features

✅ **AI-Powered Search** - Natural language queries like *"Find gyms in Austin without websites"*  
✅ **Multi-Source Scraping** - Searches Google Maps, web, and scrapes any site  
✅ **LangGraph Agents** - Supervisor pattern with specialized agents  
✅ **Local Storage** - SQLite database, no cloud required  
✅ **Multi-Tab UI** - Scraper, Lead Database, Sales (coming soon)  
✅ **Future-Ready** - Built to add voice agents, sales automation, and more  

---

## Quick Start

### 1. Install Dependencies

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Install Playwright (for web scraping)

```bash
playwright install chromium
```

### 3. Configure API Keys

Create a `.env` file (copy from `.env.example`):

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
# Required
OPENAI_API_KEY=sk-proj-...
SERPAPI_KEY=...          # For Google Maps search
TAVILY_API_KEY=...       # For web search

# Optional
ANTHROPIC_API_KEY=...
```

### 4. Run the App

```bash
streamlit run app.py
```

Open your browser to `http://localhost:8501`

---

## Example Queries

Try these in the Scraper tab:

- **"Find gyms in Austin without websites"**
- **"All wedding-related businesses within 5km of Miami"**
- **"Companies that just got Series A funding"**
- **"Real estate agencies on Google Maps without active websites"**
- **"YC-backed startups hiring AI engineers"**

---

## Architecture

### LangGraph Supervisor Pattern

```
User Query → Supervisor (Plans) → Maps/Web Search → Scraper → Supervisor → Results
```

**Agents:**
- **Supervisor**: Analyzes query, creates plan, routes to other agents
- **Maps Searcher**: Searches Google Maps for local businesses
- **Web Searcher**: General web search for companies, news, etc.
- **Scraper**: Extracts structured data from websites using AI

**Tools:**
- Google Maps Search (SerpAPI)
- Web Search (Tavily)
- Advanced Web Scraper (Crawl4AI)
- Website Validator

---

## Project Structure

```
/Super-Scraper
├── app.py                  # Streamlit UI
├── config.py               # Configuration
├── database.py             # SQLite models
├── requirements.txt
├── .env.example
│
├── agents/
│   ├── state.py           # Shared state
│   ├── supervisor.py      # Main orchestrator
│   ├── scraper.py         # Scraping agent
│   ├── search_agents.py   # Maps & web search
│   └── graph.py           # LangGraph workflow
│
├── tools/
│   ├── maps_search.py     # Google Maps API
│   ├── web_search.py      # Tavily API
│   ├── scraper.py         # Crawl4AI
│   └── validator.py       # URL validator
│
└── data/
    ├── scraper.db         # SQLite database
    └── checkpoints.db     # LangGraph state
```

---

## API Keys

### Required APIs

1. **OpenAI** - For AI reasoning and extraction
   - Get key: https://platform.openai.com/api-keys
   - Free tier: $5 credit

2. **SerpAPI** - For Google Maps search
   - Get key: https://serpapi.com/
   - Free tier: 100 searches/month

3. **Tavily** - For web search
   - Get key: https://tavily.com/
   - Free tier: 1000 searches/month

### Optional APIs

- **Anthropic** - Alternative to OpenAI (Claude)
- **Firecrawl** - Premium web scraping

---

## Future Enhancements

- [ ] **Sales Team Agent** - Automated outreach
- [ ] **Voice Caller Agent** - ElevenLabs integration
- [ ] **Calendar Scheduler** - Book meetings automatically
- [ ] **Lead Scoring** - AI-powered qualification
- [ ] **Email Enrichment** - Find contact emails
- [ ] **CRM Integration** - Sync with HubSpot, Salesforce

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| **AI Orchestration** | LangGraph |
| **AI Models** | OpenAI GPT-4o |
| **Web Scraping** | Crawl4AI, Playwright |
| **Search** | SerpAPI, Tavily |
| **Database** | SQLite |
| **Frontend** | Streamlit |
| **Backend** | Python 3.10+ |

---

## License

MIT

---

## Support

For issues or questions, please open a GitHub issue.

**Happy Scraping! 🚀**
