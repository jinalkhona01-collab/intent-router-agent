# 🛒 E-Commerce Intent Router Agent

An AI-powered customer support agent built with **Google ADK** and **Gemini 2.5 Flash**, deployed as a serverless endpoint on **Google Cloud Run**.

The agent reads a customer's natural language message, classifies the intent behind it, and routes it to the correct fixed support response — instantly, with zero hallucination risk.

---

## 💡 What it does

A customer types something like:
> *"Hey, where is my order? I placed it 3 days ago."*

The agent:
1. Reads the message using Gemini 2.5 Flash
2. Classifies it as `order_status`
3. Calls the `route_intent` tool
4. Returns the correct pre-approved support response

---

## 🎯 Supported Intents

| Intent | Triggered by |
|---|---|
| `order_status` | Questions about order location or delivery |
| `return_request` | Requests to return or exchange an item |
| `shipping_info` | Questions about delivery times or shipping options |
| `payment_issue` | Payment failures, billing problems, charge disputes |
| `general_inquiry` | Anything else |

---

## 🏗️ Architecture

```
User Message
     │
     ▼
Cloud Run (intent-router)
     │
     ▼
ADK Runner + Session
     │
     ▼
Gemini 2.5 Flash (via Vertex AI)
  [classifies intent]
     │
     ▼
route_intent tool
  [looks up fixed response]
     │
     ▼
JSON Response
{
  "intent": "order_status",
  "response": "To check your order status..."
}
```

---

## 📁 Project Structure

```
intent_router_agent/
├── intent_router/
│   ├── __init__.py       # ADK package entry point
│   └── agent.py          # root_agent + route_intent tool
├── requirements.txt      # Python dependencies
└── .env                  # Environment variables (local only, not committed)
```

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| [Google ADK](https://google.github.io/adk-docs/) `v1.14.0` | Agent framework |
| Gemini 2.5 Flash | Intent classification via Vertex AI |
| Google Cloud Run | Serverless deployment |
| Google Cloud Build | Automated container builds |
| Google Artifact Registry | Docker image storage |
| Google Cloud Logging | Runtime logging |
| Vertex AI | Gemini inference backend |
| Python 3.11 | Core language |
| `python-dotenv` | Environment variable management |
| `uv` | Fast Python package manager |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) installed
- A GCP project with the following APIs enabled:

```bash
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  aiplatform.googleapis.com \
  compute.googleapis.com
```

---

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/intent-router-agent.git
cd intent-router-agent
```

### 2. Create and activate virtual environment

```bash
uv venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
uv pip install -r requirements.txt
```

### 4. Set up environment variables

```bash
PROJECT_ID=$(gcloud config get-value project)
REGION="us-central1"

cat <<EOF > .env
PROJECT_ID=$PROJECT_ID
REGION=$REGION
MODEL="gemini-2.5-flash"
GOOGLE_CLOUD_PROJECT=$PROJECT_ID
GOOGLE_CLOUD_LOCATION=$REGION
GOOGLE_GENAI_USE_VERTEXAI=true
EOF

source .env
```

### 5. Authenticate with GCP

```bash
gcloud auth login
gcloud auth application-default login
gcloud auth application-default set-quota-project $PROJECT_ID
```

### 6. Grant Vertex AI access to Cloud Run service account

```bash
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/aiplatform.user"
```

---

## 🧪 Test Locally

```bash
adk web
```

Open the ADK Web UI at `http://localhost:8080` and try these messages:

```
"Where is my order?"
"I want to return my shoes"
"How long does shipping take?"
"My payment failed"
"Do you have gift cards?"
```

---

## ☁️ Deploy to Cloud Run

```bash
source .env

uvx --from google-adk==1.14.0 \
adk deploy cloud_run \
  --project=$PROJECT_ID \
  --region=$REGION \
  --service_name=intent-router \
  --with_ui \
  intent_router
```

ADK will automatically:
- Build the Docker container via Cloud Build
- Push it to Artifact Registry
- Deploy it to Cloud Run
- Return a live HTTPS URL

---

## 📬 Sample API Call

```bash
curl -X POST https://YOUR-CLOUD-RUN-URL/run \
  -H "Content-Type: application/json" \
  -d '{"message": "Where is my order?"}'
```

**Response:**
```json
{
  "intent": "order_status",
  "response": "To check your order status, please visit your account at https://shop.example.com/orders or contact us at orders@example.com with your order ID."
}
```

---

## 📚 What I Learned

- How to structure a Python project for ADK deployment
- How to implement a tool-using agent with Google ADK and `ToolContext`
- The difference between AI Studio auth and Vertex AI auth in production
- How to deploy a serverless AI agent to Cloud Run using `adk deploy`
- Why combining Gemini's NLU with deterministic routing eliminates hallucination risk
- How `GOOGLE_GENAI_USE_VERTEXAI=true` switches ADK's backend from AI Studio to Vertex AI

---

## 🎓 Built as part of

**Gen AI Academy APAC Edition** — Track: Designing, building, and deploying production-ready AI agents using Gemini and the Agent Development Kit (ADK).

---

## ⚠️ Notes

- `.env` is not committed to this repo — create it locally following Step 4 above
- The Cloud Run service incurs costs when running — delete it after use with:
  ```bash
  gcloud run services delete intent-router --region=$REGION
  ```
