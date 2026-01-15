import os
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)

# Fallback Mode - Use minimal LLMs to reduce API costs
ENABLE_FALLBACK_MODE = os.getenv("ENABLE_FALLBACK_MODE", "false").lower() == "true"

# Models
if ENABLE_FALLBACK_MODE:
    logger.info("🔄 FALLBACK MODE ENABLED - Using 1 Ollama + 2 Groq instances")
    # Fallback: 1 local Ollama + 2 Groq instances
    PRO_MODEL_1 = os.getenv("FALLBACK_PRO_MODEL_1", "ollama/qwen2.5:7B")
    PRO_MODEL_2 = os.getenv("FALLBACK_PRO_MODEL_2", "groq/llama-3.3-70b-versatile")
    CON_MODEL_1 = os.getenv("FALLBACK_CON_MODEL_1", "groq/llama-3.3-70b-versatile")
    CON_MODEL_2 = os.getenv("FALLBACK_CON_MODEL_2", "ollama/qwen2.5:7B")  # Reuse local
    JUDGE_MODEL = os.getenv("FALLBACK_JUDGE_MODEL", "ollama/qwen2.5:7B")
else:
    PRO_MODEL_1 = os.getenv("PRO_MODEL_1", "openai/gpt-4")
    PRO_MODEL_2 = os.getenv("PRO_MODEL_2", "anthropic/claude-3-5-sonnet-20241022")
    CON_MODEL_1 = os.getenv("CON_MODEL_1", "openai/gpt-4")
    CON_MODEL_2 = os.getenv("CON_MODEL_2", "anthropic/claude-3-5-sonnet-20241022")
    JUDGE_MODEL = os.getenv("JUDGE_MODEL", "anthropic/claude-3-5-sonnet-20241022")

# API Keys
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Ollama endpoints
OLLAMA_LOCAL_URL = os.getenv("OLLAMA_LOCAL_URL", "http://127.0.0.1:11434")
OLLAMA_REMOTE_URL = os.getenv("OLLAMA_REMOTE_URL", "https://a47e26a32eaf.ngrok-free.app")

# Web Search
SEARCH_ENGINE = os.getenv("SEARCH_ENGINE", "duckduckgo")
MAX_SEARCH_RESULTS = int(os.getenv("MAX_SEARCH_RESULTS", "8"))
MAX_SCRAPED_PAGES_PER_FACTOR = int(os.getenv("MAX_SCRAPED_PAGES_PER_FACTOR", "5"))
SCRAPE_TIMEOUT = int(os.getenv("SCRAPE_TIMEOUT", "15"))

# Debate
DEBATE_ROUNDS = int(os.getenv("DEBATE_ROUNDS", "3"))
MAX_ARGUMENT_LENGTH = int(os.getenv("MAX_ARGUMENT_LENGTH", "200"))
ALLOW_CROSS_CRITIQUE = os.getenv("ALLOW_CROSS_CRITIQUE", "true").lower() == "true"
MAX_FACTORS = int(os.getenv("MAX_FACTORS", "5"))

# Rate Limiting
REQUEST_DELAY_SECONDS = float(os.getenv("REQUEST_DELAY_SECONDS", "0.5"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
RETRY_BACKOFF_FACTOR = float(os.getenv("RETRY_BACKOFF_FACTOR", "2.0"))

# Provider-specific delays (to avoid rate limits)
GROQ_DELAY_SECONDS = float(os.getenv("GROQ_DELAY_SECONDS", "2.0"))  # Longer delay for Groq
OLLAMA_DELAY_SECONDS = float(os.getenv("OLLAMA_DELAY_SECONDS", "0.1"))  # Minimal for local
OPENAI_DELAY_SECONDS = float(os.getenv("OPENAI_DELAY_SECONDS", "1.0"))
ANTHROPIC_DELAY_SECONDS = float(os.getenv("ANTHROPIC_DELAY_SECONDS", "1.0"))

# Evaluation
ENABLE_ANONYMIZATION = os.getenv("ENABLE_ANONYMIZATION", "true").lower() == "true"
SCORING_SCALE = os.getenv("SCORING_SCALE", "1-10")

# Output
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "outputs/")
SAVE_TRANSCRIPTS = os.getenv("SAVE_TRANSCRIPTS", "true").lower() == "true"
