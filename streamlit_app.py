import streamlit as st
import requests
import time
import json

# Configuration
API_BASE_URL = "http://localhost:8000"  # Change to your ngrok URL if needed

# Headers for ngrok (bypasses browser warning)
HEADERS = {
    "Content-Type": "application/json",
    "ngrok-skip-browser-warning": "true"
}

st.set_page_config(page_title="Project AETHER", page_icon="⚔️", layout="wide")

# Custom CSS
st.markdown("""
<style>
.big-font {font-size:24px !important; font-weight:bold;}
.score-box {padding:10px; border-radius:5px; background-color:#f0f2f6; margin:5px 0;}
.verdict-positive {color:#28a745; font-weight:bold;}
.verdict-negative {color:#dc3545; font-weight:bold;}
.verdict-neutral {color:#ffc107; font-weight:bold;}
</style>
""", unsafe_allow_html=True)

st.title("⚔️ Project AETHER - Adversarial Debate Analysis")
st.markdown("*Stress-test your ideas through AI-powered adversarial debate*")

# Main input section
st.header("📄 Input Your Proposal")

col1, col2 = st.columns([3, 1])
with col1:
    input_method = st.radio("Choose input method:", ["Text Input", "Upload .txt File"])
with col2:
    enable_scraping = st.toggle("Enable Web Scraping", value=False, help="Collect evidence from the web (slower but more thorough)")

report_text = ""
if input_method == "Text Input":
    report_text = st.text_area("Enter your proposal:", height=200, 
                                placeholder="Paste your proposal here...")
else:
    uploaded_file = st.file_uploader("Upload a .txt file", type=['txt'])
    if uploaded_file:
        report_text = uploaded_file.read().decode('utf-8')
        st.text_area("File contents:", value=report_text, height=200)

# Initialize session state
if 'doc_id' not in st.session_state:
    st.session_state.doc_id = None
if 'factors' not in st.session_state:
    st.session_state.factors = []
if 'factor_results' not in st.session_state:
    st.session_state.factor_results = {}
if 'synthesis' not in st.session_state:
    st.session_state.synthesis = None

# Analysis button
if st.button("🚀 Start Analysis", type="primary", disabled=not report_text):
    with st.spinner("Uploading document and extracting factors..."):
        try:
            # Step 1: Upload document
            response = requests.post(
                f"{API_BASE_URL}/upload",
                json={"report_text": report_text, "enable_web_scraping": enable_scraping},
                headers=HEADERS,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            st.session_state.doc_id = data['document_id']
            st.session_state.factors = data['factors']
            st.session_state.factor_results = {}
            st.session_state.synthesis = None
            
            st.success(f"✅ Document uploaded! ID: {st.session_state.doc_id}")
            st.info(f"📊 Extracted {data['total_factors']} factors")
            
        except Exception as e:
            st.error(f"❌ Upload failed: {str(e)}")

# Display factors and analyze
if st.session_state.doc_id and st.session_state.factors:
    st.markdown("---")
    st.header("🔍 Extracted Factors")
    
    for factor in st.session_state.factors:
        factor_id = factor['id']
        factor_title = factor['title']
        
        with st.expander(f"**Factor {factor_id}: {factor_title}**", expanded=True):
            col1, col2 = st.columns([3, 1])
            
            with col2:
                if st.button(f"Analyze Factor {factor_id}", key=f"analyze_{factor_id}"):
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    try:
                        # Start analysis
                        status_text.text("🚀 Starting analysis...")
                        progress_bar.progress(10)
                        
                        response = requests.post(
                            f"{API_BASE_URL}/analyze/factor/{st.session_state.doc_id}/{factor_id}",
                            headers=HEADERS,
                            timeout=300  # 5 min timeout for long debates
                        )
                        response.raise_for_status()
                        result = response.json()
                        
                        st.session_state.factor_results[factor_id] = result
                        
                        progress_bar.progress(100)
                        status_text.text("✅ Analysis complete!")
                        time.sleep(1)
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Analysis failed: {str(e)}")
            
            # Display results if available
            if factor_id in st.session_state.factor_results:
                result = st.session_state.factor_results[factor_id]
                
                # Check if analysis is complete
                if result.get('status') == 'complete' and 'agent_responses' in result:
                    # Agent Responses
                    st.subheader("💬 Agent Arguments")
                    cols = st.columns(2)
                    for i, agent in enumerate(result['agent_responses']):
                        with cols[i % 2]:
                            side = "🟢 PRO" if "Pro" in agent['agent_id'] else "🔴 CON"
                            st.markdown(f"**{side} - {agent['agent_id']}**")
                            st.text_area("", value=agent['response'], height=150, key=f"agent_{factor_id}_{i}", disabled=True)
                
                    # Debate Summary
                    st.subheader("⚔️ Debate Summary")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**🟢 Pro Arguments**")
                        st.write(result['debate']['pro_argument'])
                    with col2:
                        st.markdown("**🔴 Con Arguments**")
                        st.write(result['debate']['con_argument'])
                    
                    # Judge Verdict
                    st.subheader("⚖️ Judge's Verdict")
                    verdict = result['debate']['judge_verdict']
                    
                    # Color code verdict - strict categorization
                    verdict_text = verdict['verdict']
                    verdict_lower = verdict_text.lower()
                    
                    # Check for neutral/banned words
                    neutral_words = ['neutral', 'mixed', 'balanced', 'inconclusive', 'both sides', 'further analysis', 'unclear']
                    if any(word in verdict_lower for word in neutral_words):
                        st.error("⚠️ WARNING: Judge gave a NEUTRAL verdict (this should not happen!)")
                        st.markdown(f"<p class='verdict-neutral'>❓ {verdict_text}</p>", unsafe_allow_html=True)
                    
                    # Positive verdict detection
                    elif any(word in verdict_lower for word in ['positive', 'achievable', 'feasible', 'recommended', 'proceed', 'viable', 'strong', 'supports']):
                        st.markdown(f"<p class='verdict-positive'>✅ {verdict_text}</p>", unsafe_allow_html=True)
                    
                    # Negative verdict detection
                    elif any(word in verdict_lower for word in ['negative', 'not feasible', 'high risk', 'not recommended', 'oppose', 'reject', 'fails', 'insufficient']):
                        st.markdown(f"<p class='verdict-negative'>❌ {verdict_text}</p>", unsafe_allow_html=True)
                    
                    # Fallback if no clear keywords found
                    else:
                        st.warning(f"⚠️ Ambiguous verdict detected: {verdict_text}")
                        st.markdown(f"<p class='verdict-neutral'>❓ {verdict_text}</p>", unsafe_allow_html=True)
                    
                    st.markdown(f"**Reasoning:** {verdict['reasoning']}")
                    st.markdown(f"**Confidence:** {verdict['confidence']}/10")
                    
                    # Peer Review Scores
                    st.subheader("📊 Peer Review Scores")
                    score_cols = st.columns(len(result['debate']['peer_review_scores']))
                    for i, score in enumerate(result['debate']['peer_review_scores']):
                        with score_cols[i]:
                            st.metric(score['agent_id'], f"{score['score']:.1f}/10")
                
                elif result.get('status') == 'error':
                    st.error(f"❌ Analysis failed: {result.get('error', 'Unknown error')}")
                else:
                    st.info("⏳ Analysis in progress...")

# Synthesis button
if st.session_state.doc_id and st.session_state.factors:
    completed = len(st.session_state.factor_results)
    total = len(st.session_state.factors)
    
    st.markdown("---")
    st.header("📊 Final Synthesis")
    
    if completed < total:
        st.warning(f"⚠️ Analyze all factors first ({completed}/{total} complete)")
    else:
        if st.button("🎯 Generate Final Synthesis", type="primary"):
            with st.spinner("Generating final synthesis..."):
                try:
                    response = requests.get(
                        f"{API_BASE_URL}/synthesis/{st.session_state.doc_id}",
                        headers=HEADERS,
                        timeout=60
                    )
                    response.raise_for_status()
                    st.session_state.synthesis = response.json()
                    st.success("✅ Synthesis complete!")
                    
                except Exception as e:
                    st.error(f"❌ Synthesis failed: {str(e)}")

# Display synthesis
if st.session_state.synthesis:
    st.markdown("---")
    synthesis = st.session_state.synthesis
    
    # Overall Recommendation
    rec = synthesis['overall_recommendation']
    if rec == "PROCEED_WITH_CAUTION":
        st.success(f"### ✅ {rec}")
    elif rec == "HIGH_RISK":
        st.error(f"### ❌ {rec}")
    else:
        st.warning(f"### ⚠️ {rec}")
    
    # Executive Summary
    st.subheader("Executive Summary")
    st.info(synthesis['executive_summary'])
    
    # Key Findings
    st.subheader("🔑 Key Findings")
    for i, finding in enumerate(synthesis['key_findings'], 1):
        st.markdown(f"**{i}.** {finding}")
    
    # Meta Analysis
    st.subheader("📈 Meta Analysis")
    st.write(synthesis['meta_analysis'])
    
    # Markdown Report
    if 'markdown_report' in synthesis:
        st.markdown("---")
        st.subheader("📄 Full Report")
        
        # Download button
        st.download_button(
            label="📥 Download Full Report",
            data=synthesis['markdown_report'],
            file_name=f"aether_report_{st.session_state.doc_id}.md",
            mime="text/markdown"
        )
        
        # Show preview
        with st.expander("Preview Full Report"):
            st.markdown(synthesis['markdown_report'])

# Footer
st.markdown("---")
st.markdown("*Project AETHER - Adversarial Debate Analysis System*")
