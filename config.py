import os
from dotenv import load_dotenv

load_dotenv()

# Models
PRO_MODEL_1 = os.getenv("PRO_MODEL_1", "openai/gpt-4")
PRO_MODEL_2 = os.getenv("PRO_MODEL_2", "anthropic/claude-3-5-sonnet-20241022")
CON_MODEL_1 = os.getenv("CON_MODEL_1", "openai/gpt-4")
CON_MODEL_2 = os.getenv("CON_MODEL_2", "anthropic/claude-3-5-sonnet-20241022")
JUDGE_MODEL = os.getenv("JUDGE_MODEL", "anthropic/claude-3-5-sonnet-20241022")

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")

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

# Evaluation
ENABLE_ANONYMIZATION = os.getenv("ENABLE_ANONYMIZATION", "true").lower() == "true"
SCORING_SCALE = os.getenv("SCORING_SCALE", "1-10")

# Output
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "outputs/")
SAVE_TRANSCRIPTS = os.getenv("SAVE_TRANSCRIPTS", "true").lower() == "true"
