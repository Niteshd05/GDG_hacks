import re
import json
from llm_client import call_llm
import config
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)

def anonymize_transcript(transcript):
    """
    Remove model names and role labels from transcript.
    Keep agent IDs but make them generic.
    """
    if not config.ENABLE_ANONYMIZATION:
        return transcript
    
    # Replace Pro-A, Pro-B, Con-A, Con-B with Agent-1, Agent-2, Agent-3, Agent-4
    anonymized = transcript.replace("Pro-A", "Agent-1")
    anonymized = anonymized.replace("Pro-B", "Agent-2")
    anonymized = anonymized.replace("Con-A", "Agent-3")
    anonymized = anonymized.replace("Con-B", "Agent-4")
    
    # Remove role labels
    anonymized = re.sub(r'\(PRO\)', '', anonymized)
    anonymized = re.sub(r'\(CON\)', '', anonymized)
    
    return anonymized

def peer_review(anonymized_transcript, reviewer_model):
    """
    Have a model review the entire debate and provide scores and critique.
    Returns dict with scores and written critique.
    """
    system_prompt = """You are a debate evaluator. Score each agent's performance.

Return ONLY valid JSON with these exact fields (1-10 scale):
{
  "Agent-1": {"reasoning": 7, "bias": 6, "insight": 8, "evidence": 7, "debate_skill": 8, "critique": "Strong logic"},
  "Agent-2": {"reasoning": 6, "bias": 7, "insight": 6, "evidence": 6, "debate_skill": 7, "critique": "Moderate"},
  "Agent-3": {"reasoning": 7, "bias": 6, "insight": 7, "evidence": 8, "debate_skill": 6, "critique": "Good evidence"},
  "Agent-4": {"reasoning": 6, "bias": 8, "insight": 6, "evidence": 7, "debate_skill": 7, "critique": "Some bias"}
}"""

    prompt = f"""Review this debate and score each agent (1-10):

{anonymized_transcript[:2000]}

Return ONLY the JSON object, no other text. Start with {{ and end with }}."""

    response = call_llm(reviewer_model, prompt, system_prompt)
    
    try:
        # Try to parse JSON directly
        response_clean = response.strip()
        
        # Handle empty response
        if not response_clean:
            logger.warning(f"⚠️ Empty response from {reviewer_model}")
            raise ValueError("Empty response")
        
        # Try to extract JSON if wrapped in markdown code blocks
        if "```json" in response_clean:
            start = response_clean.find("```json") + 7
            end = response_clean.find("```", start)
            response_clean = response_clean[start:end].strip()
        elif "```" in response_clean:
            start = response_clean.find("```") + 3
            end = response_clean.find("```", start)
            response_clean = response_clean[start:end].strip()
        
        # Try to find JSON object in the response
        if "{" in response_clean and "}" in response_clean:
            start = response_clean.find("{")
            end = response_clean.rfind("}") + 1
            response_clean = response_clean[start:end]
        
        logger.debug(f"Parsed response: {response_clean[:200]}...")
        scores = json.loads(response_clean)
        
        # Validate structure
        if not isinstance(scores, dict):
            raise ValueError("Response is not a dict")
        
        logger.info(f"✓ Successfully parsed peer review from {reviewer_model}")
        return scores
    except Exception as e:
        # Fallback: return empty scores
        logger.warning(f"⚠️ Failed to parse peer review from {reviewer_model}: {e}")
        logger.debug(f"Raw response: {response[:300]}...")
        return {
            f"Agent-{i}": {
                "reasoning": 5, "bias": 5, "insight": 5, 
                "evidence": 5, "debate_skill": 5, 
                "critique": "Unable to parse review"
            } for i in range(1, 5)
        }

def collect_peer_reviews(anonymized_transcript):
    """
    Collect peer reviews from all models including the judge.
    Returns aggregated review data.
    """
    all_models = [
        config.PRO_MODEL_1,
        config.PRO_MODEL_2,
        config.CON_MODEL_1,
        config.CON_MODEL_2,
        config.JUDGE_MODEL
    ]
    
    logger.info(f"📊 Collecting peer reviews from {len(all_models)} models...")
    reviews = {}
    
    # Collect reviews in parallel
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_model = {
            executor.submit(peer_review, anonymized_transcript, model): model
            for model in all_models
        }
        
        for idx, future in enumerate(as_completed(future_to_model), 1):
            model = future_to_model[future]
            logger.info(f"→ Review {idx}/{len(all_models)}: {model}")
            try:
                review = future.result()
                reviews[model] = review
                logger.info(f"✓ Review complete from {model}")
            except Exception as e:
                logger.error(f"❌ Review failed from {model}: {e}")
                # Add fallback review
                reviews[model] = {
                    f"Agent-{i}": {
                        "reasoning": 5, "bias": 5, "insight": 5, 
                        "evidence": 5, "debate_skill": 5, 
                        "critique": f"Review failed: {str(e)}"
                    } for i in range(1, 5)
                }
    
    logger.info(f"✓ All peer reviews collected")
    return reviews
