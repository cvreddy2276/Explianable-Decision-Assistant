# Explainable Decision Assistant for Operational Systems

A complete multi-agent AI course project that explains operational decisions in simple language. It uses LangGraph for orchestration, LangChain and OpenRouter for LLM access, LangSmith for tracing and evaluation, FastAPI for the API, and Streamlit for the interface.

## Project structure

```text
ExplainableDecisionAssistant/
├── backend/
│   ├── agents/
│   │   ├── explanation_agent.py
│   │   ├── fairness_agent.py
│   │   ├── transparency_agent.py
│   │   └── summary_agent.py
│   ├── graph.py
│   ├── models.py
│   └── main.py
├── frontend/app.py
├── evaluation/langsmith_evaluation.py
├── sample_data/decisions.json
├── requirements.txt
└── README.md
```

## Requirements

- Python 3.11+
- OpenRouter API key
- Optional LangSmith API key for tracing and evaluation

## Installation

```powershell
cd D:\agentic_ai\ExplainableDecisionAssistant
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Create a `.env` file manually in the project root:

```dotenv
OPENROUTER_API_KEY=your_openrouter_key
LANGCHAIN_API_KEY=your_langsmith_key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=ExplainableDecisionAssistant
```

LangChain's `ChatOpenAI` integration connects to OpenRouter at `https://openrouter.ai/api/v1`; no OpenAI SDK is used directly.

## Run the FastAPI backend

```powershell
cd D:\agentic_ai\ExplainableDecisionAssistant
uvicorn backend.main:app --reload
```

- API docs: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health

### Example API request

PowerShell:

```powershell
$body = @{
    employee = "Rahul"
    experience = 5
    traffic_score = 0.3
    distance = 15
    assigned_route = "Zone A"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/explain" `
  -Method Post -ContentType "application/json" -Body $body
```

curl:

```bash
curl -X POST "http://127.0.0.1:8000/explain" \
  -H "Content-Type: application/json" \
  -d '{"employee":"Rahul","experience":5,"traffic_score":0.3,"distance":15,"assigned_route":"Zone A"}'
```

The response contains `decision_explanation`, `fairness_assessment`, `influencing_factors`, and `final_summary`.

## Run the Streamlit frontend

In a second terminal:

```powershell
cd D:\agentic_ai\ExplainableDecisionAssistant
streamlit run frontend/app.py
```

Open the URL shown by Streamlit, paste or edit the JSON, and select **Run Explanation**. The UI requires the FastAPI server on port 8000.

## LangSmith evaluation

The evaluation script runs every decision in `sample_data/decisions.json` through the graph and uses an LLM judge to score:

1. Clarity
2. Simplicity
3. Completeness
4. Transparency

```powershell
python evaluation/langsmith_evaluation.py
```

Set `LANGCHAIN_TRACING_V2=true` and `LANGCHAIN_API_KEY` to store traces in LangSmith. The script prints results and sends traced runs to the project named in `LANGCHAIN_PROJECT`.

## LangGraph workflow

```text
START -> ExplanationAgent -> FairnessAgent -> TransparencyAgent -> SummaryAgent -> END
```

## Important limitations

- Fairness results are preliminary assessments based only on supplied factors, not a legal or organizational fairness audit.
- Missing API credentials cause agents to return deterministic fallback explanations rather than LLM-generated text.
