from llm_client import call_llm
import config
import json
import logging

logger = logging.getLogger(__name__)

def judge_synthesis(factor, debate_transcript, peer_reviews):
    """
    Judge analyzes the entire debate and provides final verdict.
    Returns comprehensive synthesis including verdict, reasoning, and confidence.
    """
    logger.info(f"⚖️  Judge synthesizing verdict for: {factor}")
    
    system_prompt = """You are the Chairman and final judge of this debate.

Your responsibility is to judge the ENTIRE DEBATE, not just final turns.

You must provide:
1. VERDICT: Your final position on this factor
2. REASONING: Why this verdict holds based on debate quality
3. FAILURES: What arguments failed and why
4. POTENTIAL CHANGES: What could change the outcome
5. CONFIDENCE: Your confidence level (1-10)

Judge based on argument quality, not volume. Consider peer reviews but form your own opinion.
Be transparent and explainable."""

    # Format peer reviews summary
    peer_summary = "PEER REVIEW SUMMARY:\n"
    for model, reviews in peer_reviews.items():
        peer_summary += f"\n{model}:\n"
        for agent, scores in reviews.items():
            if isinstance(scores, dict) and 'reasoning' in scores:
                avg_score = sum([v for k, v in scores.items() if k != 'critique' and isinstance(v, (int, float))]) / 5
                peer_summary += f"  {agent}: {avg_score:.1f}/10 - {scores.get('critique', '')[:100]}\n"
    
    prompt = f"""FACTOR: {factor}

FULL DEBATE TRANSCRIPT:
{debate_transcript}

{peer_summary}

Provide your final synthesis."""

    response = call_llm(config.JUDGE_MODEL, prompt, system_prompt)
    logger.info(f"✓ Judge verdict complete for {factor}")
    return response

def generate_final_report(report_text, all_factor_results):
    """
    Generate the final comprehensive report.
    all_factor_results: list of dicts with factor, transcript, reviews, verdict
    """
    logger.info(f"📝 Generating final report with {len(all_factor_results)} factors")
    
    report = []
    report.append("# PROJECT AETHER - FINAL REPORT")
    report.append("=" * 80)
    report.append("")
    report.append("## ORIGINAL REPORT")
    report.append(report_text[:500] + "...")
    report.append("")
    report.append("=" * 80)
    report.append("")
    
    for idx, result in enumerate(all_factor_results, 1):
        logger.info(f"  Adding factor {idx}: {result['factor']}")
        report.append(f"## FACTOR {idx}: {result['factor']}")
        report.append("")
        report.append("### JUDGE'S VERDICT")
        report.append(result['verdict'])
        report.append("")
        report.append("### PEER REVIEW SCORES")
        
        # Aggregate peer scores
        for agent_num in range(1, 5):
            agent_id = f"Agent-{agent_num}"
            scores = []
            for model, reviews in result['peer_reviews'].items():
                if agent_id in reviews:
                    agent_scores = reviews[agent_id]
                    if isinstance(agent_scores, dict):
                        avg = sum([v for k, v in agent_scores.items() if k != 'critique' and isinstance(v, (int, float))]) / 5
                        scores.append(avg)
            
            if scores:
                avg_score = sum(scores) / len(scores)
                report.append(f"- {agent_id}: {avg_score:.1f}/10")
        
        report.append("")
        report.append("---")
        report.append("")
    
    report.append("=" * 80)
    report.append("## META-ANALYSIS")
    report.append("")
    report.append("This report represents a stress-test of the original proposal.")
    report.append("Verdicts are based on argument quality, not consensus.")
    report.append("All reasoning is auditable through saved transcripts.")
    report.append("")
    report.append("=" * 80)
    
    logger.info(f"✓ Report generated successfully")
    return "\n".join(report)
