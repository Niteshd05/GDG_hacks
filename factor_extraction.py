import json
from llm_client import call_llm
import config

def extract_factors(report_text):
    """
    Extract debatable factors from the input report.
    Returns a list of factor strings (limited by MAX_FACTORS config).
    """
    system_prompt = """You are a critical analyst. Your task is to break down reports into independent, debatable factors.

Rules:
- Each factor must be arguable from both sides
- Factors must be non-overlapping
- Prefer analytical dimensions over topics
- Examples: Feasibility, Scalability, Risk profile, Ethical implications, Market fit

Return ONLY a JSON array of strings, nothing else."""

    prompt = f"""Analyze the following report and extract -{config.MAX_FACTORS} debatable factors:

{report_text}

Return a JSON array like: ["Factor 1", "Factor 2", "Factor 3"]"""

    response = call_llm(config.CON_MODEL_2, prompt, system_prompt)
    
    # Parse JSON response
    try:
        factors = json.loads(response.strip())
        if isinstance(factors, list) and all(isinstance(f, str) for f in factors):
            return factors[:config.MAX_FACTORS]
        else:
            raise ValueError("Invalid factor format")
    except:
        # Fallback: try to extract from response
        lines = [line.strip(' "-,[]') for line in response.strip().split('\n') if line.strip()]
        return [line for line in lines if line and not line.startswith('{')][:config.MAX_FACTORS]
