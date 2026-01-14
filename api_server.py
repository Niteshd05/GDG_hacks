#!/usr/bin/env python3
"""
FastAPI server for Project AETHER
Provides REST API endpoints for frontend integration.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import os
import uuid
import logging
from datetime import datetime
from typing import Optional, Dict, List

import config
from factor_extraction import extract_factors
from evidence_collector import collect_all_evidence
from debate_engine import run_debate
from peer_review import anonymize_transcript, collect_peer_reviews
from judge import judge_synthesis, generate_final_report

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Project AETHER API", version="1.0.0")

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for analysis jobs
# In production, use a database
analysis_jobs: Dict[str, dict] = {}

class AnalysisRequest(BaseModel):
    report_text: str

class AnalysisResponse(BaseModel):
    job_id: str
    status: str
    message: str

class StatusResponse(BaseModel):
    job_id: str
    status: str
    progress: Optional[str] = None
    current_factor: Optional[int] = None
    total_factors: Optional[int] = None
    result: Optional[dict] = None
    error: Optional[str] = None

def ensure_output_dir():
    """Create output directory if it doesn't exist."""
    if not os.path.exists(config.OUTPUT_DIR):
        os.makedirs(config.OUTPUT_DIR)

def run_analysis(job_id: str, report_text: str):
    """
    Run the complete AETHER analysis pipeline.
    Updates job status as it progresses.
    """
    try:
        ensure_output_dir()
        
        # Update status
        analysis_jobs[job_id]["status"] = "running"
        analysis_jobs[job_id]["progress"] = "Extracting factors"
        
        # Extract factors
        factors = extract_factors(report_text)
        analysis_jobs[job_id]["total_factors"] = len(factors)
        analysis_jobs[job_id]["factors"] = factors
        
        # Process each factor
        all_factor_results = []
        
        for idx, factor in enumerate(factors, 1):
            analysis_jobs[job_id]["current_factor"] = idx
            analysis_jobs[job_id]["progress"] = f"Processing factor {idx}/{len(factors)}: {factor}"
            
            # Collect evidence
            evidence = collect_all_evidence(factor)
            
            # Run debate
            debate_transcript = run_debate(report_text, factor, evidence)
            
            # Save transcript
            if config.SAVE_TRANSCRIPTS:
                transcript_path = os.path.join(config.OUTPUT_DIR, f"debate_{job_id}_factor_{idx}.txt")
                with open(transcript_path, 'w', encoding='utf-8') as f:
                    f.write(debate_transcript)
            
            # Anonymize
            anonymized_transcript = anonymize_transcript(debate_transcript)
            
            # Peer review
            peer_reviews = collect_peer_reviews(anonymized_transcript)
            
            # Judge synthesis
            verdict = judge_synthesis(factor, debate_transcript, peer_reviews)
            
            all_factor_results.append({
                'factor': factor,
                'transcript': debate_transcript,
                'peer_reviews': peer_reviews,
                'verdict': verdict
            })
        
        # Generate final report
        analysis_jobs[job_id]["progress"] = "Generating final report"
        logger.info(f"📝 Generating final report...")
        final_report = generate_final_report(report_text, all_factor_results)
        
        # Save outputs
        logger.info(f"💾 Saving output files...")
        report_path = os.path.join(config.OUTPUT_DIR, f"final_report_{job_id}.md")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(final_report)
        
        reviews_path = os.path.join(config.OUTPUT_DIR, f"peer_review_{job_id}.json")
        with open(reviews_path, 'w', encoding='utf-8') as f:
            reviews_data = {
                f"factor_{i+1}": {
                    'factor': result['factor'],
                    'reviews': result['peer_reviews']
                }
                for i, result in enumerate(all_factor_results)
            }
            json.dump(reviews_data, f, indent=2)
        
        logger.info(f"✅ Analysis complete! Saved to {report_path}")
        
        # Update final status
        analysis_jobs[job_id]["status"] = "completed"
        analysis_jobs[job_id]["progress"] = "Analysis complete"
        analysis_jobs[job_id]["result"] = {
            "final_report": final_report,
            "factors": [
                {
                    "factor": r["factor"],
                    "verdict": r["verdict"],
                    "peer_reviews": r["peer_reviews"]
                }
                for r in all_factor_results
            ],
            "report_path": report_path,
            "reviews_path": reviews_path
        }
        
    except Exception as e:
        analysis_jobs[job_id]["status"] = "failed"
        analysis_jobs[job_id]["error"] = str(e)
        analysis_jobs[job_id]["progress"] = f"Error: {str(e)}"

@app.get("/")
def root():
    """API health check."""
    return {
        "service": "Project AETHER API",
        "version": "1.0.0",
        "status": "running"
    }

@app.post("/analyze", response_model=AnalysisResponse)
def submit_analysis(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """
    Submit a report for analysis.
    Returns a job_id to track progress.
    """
    if not request.report_text or len(request.report_text.strip()) < 50:
        raise HTTPException(status_code=400, detail="Report text must be at least 50 characters")
    
    # Create job
    job_id = str(uuid.uuid4())
    analysis_jobs[job_id] = {
        "job_id": job_id,
        "status": "queued",
        "created_at": datetime.now().isoformat(),
        "report_text": request.report_text,
        "progress": "Queued for processing"
    }
    
    # Start background task
    background_tasks.add_task(run_analysis, job_id, request.report_text)
    
    return AnalysisResponse(
        job_id=job_id,
        status="queued",
        message="Analysis started. Use /status/{job_id} to check progress."
    )

@app.get("/status/{job_id}", response_model=StatusResponse)
def get_status(job_id: str):
    """
    Get the status of an analysis job.
    """
    if job_id not in analysis_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = analysis_jobs[job_id]
    
    return StatusResponse(
        job_id=job_id,
        status=job["status"],
        progress=job.get("progress"),
        current_factor=job.get("current_factor"),
        total_factors=job.get("total_factors"),
        result=job.get("result"),
        error=job.get("error")
    )

@app.get("/jobs")
def list_jobs():
    """
    List all analysis jobs.
    """
    return {
        "jobs": [
            {
                "job_id": job_id,
                "status": job["status"],
                "created_at": job["created_at"],
                "progress": job.get("progress")
            }
            for job_id, job in analysis_jobs.items()
        ]
    }

@app.delete("/job/{job_id}")
def delete_job(job_id: str):
    """
    Delete an analysis job from memory.
    """
    if job_id not in analysis_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    del analysis_jobs[job_id]
    return {"message": "Job deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
