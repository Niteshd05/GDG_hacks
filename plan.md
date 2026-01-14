# Project AETHER — Complete Project Plan

## 1. Purpose

Project AETHER is a **multi-agent debate, evidence-grounded reasoning system** designed to pressure-test reports, ideas, or proposals through structured adversarial debate, anonymous peer review, and holistic judgment.

The system enforces:

* Real argument–rebuttal–counter‑rebuttal cycles
* Evidence augmentation via live web search
* Bias exposure through anonymized peer review
* Final synthesis based on **entire debate quality**, not last-turn dominance

This is not a summarizer. It is a **reasoning stress-test pipeline**.

---

## 2. Core Design Principles

1. **Conflict before synthesis**
2. **Evidence as support, not authority**
3. **Anonymity to reduce model bias**
4. **Holistic judgment over point scoring**
5. **Transparency at every stage**

---

## 3. System Actors (LLMs)

| Role        | Count | Description                             |
| ----------- | ----- | --------------------------------------- |
| Pro Agents  | 2     | Argue in favor of each factor           |
| Con Agents  | 2     | Argue against each factor               |
| Judge Agent | 1     | Meta-evaluator and final decision maker |

All agents are **independently configurable via `.env`**.

---

## 4. High-Level Pipeline (End-to-End)

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

---

## 5. Stage-by-Stage Specification

---

### 5.1 Input Stage

**Input**

* Raw user report (plain text)

**Constraints**

* No preprocessing assumptions
* No formatting required

**Output**

* Canonical report text passed downstream

---

### 5.2 Factor Extraction Stage

**Goal**
Break the report into **independent, debatable factors**.

**Rules**

* Each factor must be arguable from both sides
* Factors must be non-overlapping
* Prefer analytical dimensions over topics

**Examples**

* Feasibility
* Scalability
* Risk profile
* Ethical implications
* Market fit

**Output**

```json
[
  "Factor 1",
  "Factor 2",
  "Factor N"
]
```

---

### 5.3 Web Search & Evidence Collection

**Search Engine**

* DuckDuckGo only

**Per Factor**
Two independent search paths:

1. **Pro Search**

   * Query intent: benefits, success cases, validation
2. **Con Search**

   * Query intent: risks, failures, criticisms

**Scraping Rules**

* JS-rendered pages allowed
* Bot-blocked pages skipped
* Content cleaned of navigation/boilerplate
* Chunked semantically

**Evidence Policy**

* Evidence augments reasoning
* Agents are penalized for quote-dumping

**Output**

* Evidence chunk list with metadata

---

### 5.4 Debate Stage (Per Factor)

**Participants**

* Pro Agent A
* Pro Agent B
* Con Agent A
* Con Agent B

**Inputs (to every agent)**

* Original report
* Factor definition
* Pro + Con evidence chunks
* Debate history so far

**Debate Mechanics**

* Configurable number of rounds
* Each round enforces:

  1. Argument
  2. Rebuttal
  3. Counter-rebuttal

**Hard Rules**

* Agents must address opponent claims
* Ignoring rebuttals is penalized later
* Repetition is penalized

**Output**

* `debate_factor_<N>.txt`

---

### 5.5 Debate Transcript Format

Each transcript contains:

* Timestamped turns
* Anonymous agent IDs
* Explicit claim–response structure

Purpose:

* Auditability
* Later blind evaluation

---

### 5.6 Anonymization Layer

**What is removed**

* Model names
* Pro/Con role labels

**What remains**

* Agent IDs (Agent X, Agent Y…)
* Full debate content

**Why**

* Prevent brand/model bias during evaluation

---

### 5.7 Peer Review & Ranking Stage

**Who Reviews**

* All 5 models (including Judge)

**What They Review**

* Entire anonymized debate transcript

**Scoring Dimensions (Per Agent)**

| Metric            | Description                               |
| ----------------- | ----------------------------------------- |
| Reasoning Quality | Logical coherence and structure           |
| Bias              | Emotional, ideological, selective framing |
| Insight           | Depth, originality, non-obvious points    |
| Evidence Use      | Accuracy, relevance, proportionality      |
| Debate Skill      | Rebuttal quality and adaptability         |

**Output**

* Numeric scores
* Written critique per agent

---

### 5.8 Chairman / Judge Synthesis

**Inputs**

* Debate transcripts
* Peer scores
* Peer critiques

**Responsibilities**

* Judge the **entire debate**, not final turns
* Identify strongest and weakest reasoning
* Surface hidden assumptions

**Final Output Must Include**

* Verdict
* Why that verdict holds
* What failed and why
* What could change the outcome
* Confidence level

---

## 6. Configuration (.env)

All behavior must be adjustable without code changes.

```env
# Models
PRO_MODEL_1=
PRO_MODEL_2=
CON_MODEL_1=
CON_MODEL_2=
JUDGE_MODEL=

# Web Search
SEARCH_ENGINE=duckduckgo
MAX_SEARCH_RESULTS=8
MAX_SCRAPED_PAGES_PER_FACTOR=5
SCRAPE_TIMEOUT=15

# Debate
DEBATE_ROUNDS=3
MAX_ARGUMENT_LENGTH=200
ALLOW_CROSS_CRITIQUE=true

# Evaluation
ENABLE_ANONYMIZATION=true
SCORING_SCALE=1-10

# Output
OUTPUT_DIR=outputs/
SAVE_TRANSCRIPTS=true
```

---

## 7. Output Artifacts

| File                | Purpose                |
| ------------------- | ---------------------- |
| debate_factor_*.txt | Full debate record     |
| peer_review.json    | Scores and critiques   |
| final_report.md     | Human-readable verdict |

---

## 8. Explicit Non-Goals

* Simple pros/cons lists
* Single-agent reasoning
* Blind trust in web sources
* Last-message-wins judgment
* Hidden or opaque reasoning

---

## 9. Success Criteria

The system is considered successful if:

* Weak arguments collapse under rebuttal
* Bias is detectable in scoring
* Judge verdict is explainable and auditable
* A reader can trace *why* a conclusion was reached

---

## 10. Summary

Project AETHER is a **reasoning crucible**.

It is designed to **stress-test beliefs**, not validate them.

Truth here is not voted.
It **survives attack**.
