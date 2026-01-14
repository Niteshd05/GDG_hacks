#!/usr/bin/env python3
"""
Rate limit testing script for Project AETHER
Tests each LLM provider with the actual usage pattern:
- 4 concurrent agent calls per round
- 2 rounds = 8 calls per factor
- 5 peer reviews per factor
"""

import time
import requests
import logging
from datetime import datetime
import statistics

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Load config
import config

# Test prompts
SHORT_PROMPT = "Write a brief 2-3 sentence technical argument about software architecture."
LONG_PROMPT = """Review this complex debate transcript and provide a JSON score:

Agent-1: Software architecture should prioritize scalability above all else. Microservices, 
containerization, and cloud-native designs are proven patterns that enable growth. Companies 
like Netflix and Uber scaled by embracing distributed systems early.

Agent-2: Over-engineering for scale is wasteful. Most startups fail before scaling becomes an issue. 
Monolithic architectures are simpler, faster to develop, and easier to reason about.

Agent-3: Indeed. The operational overhead of microservices is substantial. Kubernetes, service meshes, 
and monitoring add complexity that many teams can't handle.

Agent-4: Yet those patterns enable companies to reach billions of users. The cost of refactoring later 
is far higher than building right initially.

Provide scores for each agent on reasoning, insight, and bias (1-10)."""

def test_provider(provider, model_name, prompt, test_name, num_requests=5, delay_between=1):
    """Test a single provider with multiple sequential requests."""
    
    logger.info(f"\n{'='*80}")
    logger.info(f"Testing: {test_name}")
    logger.info(f"Provider: {provider}/{model_name}")
    logger.info(f"Requests: {num_requests} with {delay_between}s delay between")
    logger.info(f"{'='*80}")
    
    times = []
    success = 0
    failures = 0
    
    for i in range(num_requests):
        try:
            start = time.time()
            logger.info(f"\n📤 Request {i+1}/{num_requests}...")
            
            from llm_client import call_llm
            response = call_llm(f"{provider}/{model_name}", prompt)
            
            elapsed = time.time() - start
            times.append(elapsed)
            success += 1
            
            logger.info(f"✓ Success in {elapsed:.1f}s ({len(response)} chars)")
            
            if i < num_requests - 1:
                logger.info(f"⏳ Waiting {delay_between}s before next request...")
                time.sleep(delay_between)
                
        except Exception as e:
            failures += 1
            elapsed = time.time() - start
            logger.error(f"✗ Failed after {elapsed:.1f}s: {str(e)[:100]}")
            time.sleep(5)  # Wait longer after failure
    
    # Statistics
    logger.info(f"\n{'='*80}")
    logger.info(f"RESULTS for {test_name}")
    logger.info(f"{'='*80}")
    logger.info(f"Success: {success}/{num_requests}")
    logger.info(f"Failures: {failures}/{num_requests}")
    
    if times:
        logger.info(f"Min time: {min(times):.1f}s")
        logger.info(f"Max time: {max(times):.1f}s")
        logger.info(f"Avg time: {statistics.mean(times):.1f}s")
        if len(times) > 1:
            logger.info(f"Median: {statistics.median(times):.1f}s")
    
    return {
        'provider': f"{provider}/{model_name}",
        'test': test_name,
        'success': success,
        'failures': failures,
        'times': times,
        'avg_time': statistics.mean(times) if times else 0
    }

def test_concurrent_pattern():
    """
    Simulate the actual debate pattern:
    - 4 agents making requests in sequence (one round)
    - Repeat for 2 rounds to see if rate limits kick in
    """
    logger.info(f"\n\n{'#'*80}")
    logger.info(f"# SIMULATING ACTUAL DEBATE PATTERN")
    logger.info(f"# 4 agents x 2 rounds = 8 sequential requests")
    logger.info(f"{'#'*80}")
    
    agents = ['Pro-A', 'Pro-B', 'Con-A', 'Con-B']
    
    results = {}
    
    for round_num in range(1, 3):
        logger.info(f"\n🔄 ROUND {round_num}/2")
        logger.info(f"{'='*80}")
        
        for agent in agents:
            try:
                start = time.time()
                logger.info(f"\n⚔️  {agent} generating argument...")
                
                from llm_client import call_llm
                response = call_llm(config.PRO_MODEL_1, SHORT_PROMPT)
                
                elapsed = time.time() - start
                logger.info(f"✓ {agent} completed in {elapsed:.1f}s")
                
                time.sleep(0.5)  # Delay between agents in same round
                
            except Exception as e:
                logger.error(f"✗ {agent} failed: {str(e)[:100]}")
                time.sleep(3)
    
    logger.info(f"\n✓ Concurrent pattern test complete")

def test_peer_review_pattern():
    """
    Simulate peer review pattern:
    - 5 models reviewing the same transcript
    """
    logger.info(f"\n\n{'#'*80}")
    logger.info(f"# SIMULATING PEER REVIEW PATTERN")
    logger.info(f"# 5 models x 1 review = 5 sequential requests")
    logger.info(f"{'#'*80}")
    
    models = [
        config.PRO_MODEL_1,
        config.PRO_MODEL_2,
        config.CON_MODEL_1,
        config.CON_MODEL_2,
        config.JUDGE_MODEL
    ]
    
    for idx, model in enumerate(models, 1):
        try:
            start = time.time()
            logger.info(f"\n📊 Review {idx}/{len(models)}: {model}")
            
            from llm_client import call_llm
            response = call_llm(model, LONG_PROMPT)
            
            elapsed = time.time() - start
            logger.info(f"✓ Completed in {elapsed:.1f}s ({len(response)} chars)")
            
            if idx < len(models):
                time.sleep(1)  # Delay between reviews
                
        except Exception as e:
            logger.error(f"✗ Failed: {str(e)[:100]}")
            time.sleep(5)
    
    logger.info(f"\n✓ Peer review pattern test complete")

if __name__ == "__main__":
    logger.info(f"\n{'*'*80}")
    logger.info(f"PROJECT AETHER - RATE LIMIT TEST SUITE")
    logger.info(f"Started: {datetime.now().isoformat()}")
    logger.info(f"{'*'*80}")
    
    logger.info(f"\nTesting configuration:")
    logger.info(f"  Pro-A: {config.PRO_MODEL_1}")
    logger.info(f"  Pro-B: {config.PRO_MODEL_2}")
    logger.info(f"  Con-A: {config.CON_MODEL_1}")
    logger.info(f"  Con-B: {config.CON_MODEL_2}")
    logger.info(f"  Judge: {config.JUDGE_MODEL}")
    
    # Test individual providers
    logger.info(f"\n\n{'='*80}")
    logger.info(f"PHASE 1: Individual Provider Tests")
    logger.info(f"{'='*80}")
    
    test_provider("ollama", "llama3:latest", SHORT_PROMPT, "Ollama llama3 (short prompt)", num_requests=3, delay_between=2)
    test_provider("groq", "llama-3.3-70b-versatile", SHORT_PROMPT, "Groq Llama (short prompt)", num_requests=3, delay_between=2)
    test_provider("groq", "gemma2-9b-it", SHORT_PROMPT, "Groq Gemma2 (short prompt)", num_requests=2, delay_between=2)
    test_provider("ollama", "qwen2.5:7B", SHORT_PROMPT, "Ollama Qwen (Judge model, short prompt)", num_requests=2, delay_between=2)
    
    # Test concurrent pattern
    logger.info(f"\n\n{'='*80}")
    logger.info(f"PHASE 2: Concurrent Debate Pattern")
    logger.info(f"{'='*80}")
    test_concurrent_pattern()
    
    # Test peer review pattern
    logger.info(f"\n\n{'='*80}")
    logger.info(f"PHASE 3: Peer Review Pattern")
    logger.info(f"{'='*80}")
    test_peer_review_pattern()
    
    logger.info(f"\n\n{'*'*80}")
    logger.info(f"✓ ALL TESTS COMPLETE")
    logger.info(f"Completed: {datetime.now().isoformat()}")
    logger.info(f"{'*'*80}")
