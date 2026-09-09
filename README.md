# Multi-Agent Research System

A four-stage research pipeline built on LangChain and LangGraph. You give it a topic; it searches the web, scrapes the most relevant source, drafts a structured report, and then critiques its own work.

## How it works

```
topic
  │
  ├─ 1. Search agent    ── web_search (Tavily) ──▶ summary of findings
  │
  ├─ 2. Reader agent    ── extract_content (requests + BeautifulSoup) ──▶ deeper context
  │
  ├─ 3. Writer chain    ── prompt | llm | StrOutputParser ──▶ structured report
  │
  └─ 4. Critic chain    ── prompt | llm | StrOutputParser ──▶ score + feedback
```

Stages 1 and 2 are **tool-calling agents** built with `create_agent` — they decide for themselves how many times to call their tool and when to stop. Stages 3 and 4 are plain **LCEL chains**, one model call each.

Each stage's output is accumulated into a `state` dict, which `run_research_pipeline()` returns:

| Key | Produced by | Contents |
|---|---|---|
| `search_results` | search agent | Summary of what the web search turned up |
| `scraped_content` | reader agent | Text pulled from the chosen page |
| `report` | writer chain | Introduction / Key Findings / Conclusion / Sources |
| `feedback` | critic chain | Score out of 10, strengths, areas to improve |

## Files

| File | Role |
|---|---|
| [pipeline.py](pipeline.py) | Orchestration — runs the four stages in order, threads state between them. Entry point. |
| [agents.py](agents.py) | Model config, the two agent builders, and the writer/critic prompt chains. |
| [tools.py](tools.py) | The two tools: `web_search` (Tavily) and `extract_content` (scraper). |

## Setup

**1. Install dependencies**

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirement.txt
```

**2. Add API keys**

Create a `.env` file in the project root:

```
GOOGLE_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here
```

- **Google AI Studio** key (free): https://aistudio.google.com/apikey
- **Tavily** key (free tier): https://app.tavily.com

**3. Run**

```bash
python pipeline.py
```

You'll be prompted for a topic, then each stage prints its output as it completes.

```
 Enter a topic : Impact of AI on software jobs

==================================================
step 1 - search agent is working ...
==================================================
```

## Configuration

The model is set in one place, [agents.py:13](agents.py#L13):

```python
llm = ChatGoogleGenerativeAI(model="gemini-3.7-flash", temperature=0)
```

Every stage shares this instance, so changing that line switches the whole pipeline.

### Free-tier quota

The Gemini free tier allows **20 requests per day, per model**. A single pipeline run costs roughly **14 requests** — the agents loop over their tools several times each, and that adds up fast.

In practice this means **about one run per day per model**. Two ways around it:

- **Enable billing** at [aistudio.google.com](https://aistudio.google.com/) — pay-as-you-go lifts the cap, and flash models cost a fraction of a cent per run.
- **Switch models** — the quota bucket is per-model, so `gemini-3.6-flash`, `gemini-3.5-flash`, and `gemini-3.1-flash-lite` each get their own separate 20.

Note that `gemini-2.5-*` models return 404 for newly created keys; only the 3.x line is available.

## Known limitations

These are real and worth understanding before trusting the output:

- **Citations are unreliable.** The pipeline keeps only the search agent's final prose summary and discards the intermediate tool messages, which is where the actual URLs live. The writer is still instructed to list sources, so when no URLs survive it will tend to invent plausible-looking ones. **Verify any citation in the report before relying on it.**
- **Search results are truncated to 800 characters** before reaching the reader agent ([pipeline.py:33](pipeline.py#L33)). A URL appearing past that point is lost, which makes the point above more likely.
- **`web_search` has no error handling.** A Tavily failure or rate-limit raises and kills the run at stage 1. (`extract_content`, by contrast, catches its errors and returns a message.)
- **Scraping fails soft.** When a site blocks the scraper, `extract_content` returns `"could not scrape url: ..."` as normal tool output, so stage 2 degrades quietly rather than erroring.
- **No retry logic.** Transient `503 UNAVAILABLE` responses from the model API abort the whole run.

## Dependencies

Core stack, as installed:

| Package | Version |
|---|---|
| langchain | 1.4.0 |
| langchain-core | 1.6.2 |
| langgraph | 1.2.11 |
| langchain-google-genai | 4.4.0 |
| tavily-python | 0.8.1 |
| beautifulsoup4 | 4.15.0 |
| requests | 2.34.2 |
| python-dotenv | 1.2.3 |

> **Note:** `requirement.txt` is out of date — it still pins `langchain-openai` / `openai` from before the switch to Gemini, and does not list `langchain-google-genai` or `langgraph`. Installing from it alone will not produce a working environment.
