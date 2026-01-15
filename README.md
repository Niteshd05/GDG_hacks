# Project AETHER - Multi-Agent Debate System

A **multi-agent debate, evidence-grounded reasoning system** designed to pressure-test reports, ideas, or proposals through structured adversarial debate, anonymous peer review, and holistic judgment.

## Overview

Project AETHER is a reasoning stress-test pipeline that enforces:

* Real argument–rebuttal–counter‑rebuttal cycles
* Evidence augmentation via live web search
* Bias exposure through anonymized peer review
* Final synthesis based on **entire debate quality**, not last-turn dominance

This is not a summarizer. It is a **reasoning stress-test pipeline**.

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and preferences
   ```

3. **Run the system:**
   
   **Option A - Command Line:**
   ```bash
   python main.py input_report.txt
   ```
   
   **Option B - API Server (for frontend integration):**
   ```bash
   python api_server.py
   ```
   Then access the API at `http://localhost:8000`

## Configuration

All behavior is controlled via `.env` file:

- **Models**: Configure 2 Pro agents, 2 Con agents, and 1 Judge
- **Fallback Mode**: Optimized config for free tiers (1 Ollama + 2 Groq)
- **Web Search**: DuckDuckGo settings, scraping limits
- **Debate**: Number of rounds, argument length
- **Evaluation**: Anonymization, scoring scale
- **Output**: Directory and transcript saving

See `.env.example` for all options.

### Fallback Mode (Recommended for Free Tiers)

To minimize API costs and rate limits, enable fallback mode:

```bash
ENABLE_FALLBACK_MODE=true
```

**Fallback Configuration:**
- **1 Local Ollama** (qwen2.5:7B): Judge + 2 debate agents
- **2 Groq instances** (llama-3.3-70b): 2 debate agents
- **Reduced API hits**: Provider-specific delays prevent rate limits
- **Cost**: Minimal (mostly self-hosted)

This mode uses only 3 LLM instances instead of 5, reducing costs by ~60% while maintaining debate quality.

## System Actors

| Role        | Count | Description                             |
| ----------- | ----- | --------------------------------------- |
| Pro Agents  | 2     | Argue in favor of each factor           |
| Con Agents  | 2     | Argue against each factor               |
| Judge Agent | 1     | Meta-evaluator and final decision maker |

## Pipeline

```
User Report
   ↓
Factor Extraction
   ↓
For each Factor:
   ├── Web Search (Pro-oriented)
   ├── Web Search (Con-oriented)
   ├── Evidence Scraping & Chunking
   ├── Multi-Agent Debate (2 Pro, 2 Con)
   └── Debate Transcript (.txt)
   ↓
Anonymization Layer
   ↓
Peer Review & Ranking (All Agents)
   ↓
Chairman / Judge Synthesis
   ↓
Final Transparent Report
```

## Output Artifacts

| File                | Purpose                |
| ------------------- | ---------------------- |
| debate_factor_*.txt | Full debate record     |
| peer_review.json    | Scores and critiques   |
| final_report.md     | Human-readable verdict |

## Design Principles

1. **Conflict before synthesis**
2. **Evidence as support, not authority**
3. **Anonymity to reduce model bias**
4. **Holistic judgment over point scoring**
5. **Transparency at every stage**

## Requirements

- Python 3.8+
- OpenAI API key (for GPT models)
- Anthropic API key (for Claude models)
- Internet connection (for web search)

## License

MIT
