import re
import json
from llm_client import call_llm
import config

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
    system_prompt = """You are a debate evaluator. Score each agent's performance across multiple dimensions.

SCORING DIMENSIONS (1-10 scale):
- Reasoning Quality: Logical coherence and structure
- Bias: Emotional, ideological, selective framing (lower is better)
- Insight: Depth, originality, non-obvious points
- Evidence Use: Accuracy, relevance, proportionality
- Debate Skill: Rebuttal quality and adaptability

Return ONLY valid JSON in this format:
{
  "Agent-1": {"reasoning": X, "bias": X, "insight": X, "evidence": X, "debate_skill": X, "critique": "..."},
  "Agent-2": {...},
  "Agent-3": {...},
  "Agent-4": {...}
}"""

    prompt = f"""Review this anonymized debate transcript and score each agent:

{anonymized_transcript}

Provide numerical scores (1-10) and written critique for each agent."""

    response = call_llm(reviewer_model, prompt, system_prompt)
    
    try:
        # Try to parse JSON directly
        response_clean = response.strip()
        
        # Try to extract JSON if wrapped in markdown code blocks
        if "```json" in response_clean:
            start = response_clean.find("```json") + 7
            end = response_clean.find("```", start)
            response_clean = response_clean[start:end].strip()
        elif "```" in response_clean:
            start = response_clean.find("```") + 3
            end = response_clean.find("```", start)
            response_clean = response_clean[start:end].strip()
        
        scores = json.loads(response_clean)
        return scores
    except Exception as e:
        # Fallback: return empty scores
        print(f"Failed to parse peer review from {reviewer_model}: {e}")
        print(f"Response was: {response[:200]}...")
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
    
    reviews = {}
    
    for model in all_models:
        print(f"Collecting peer review from {model}...")
        review = peer_review(anonymized_transcript, model)
        reviews[model] = review
    
    return reviews
