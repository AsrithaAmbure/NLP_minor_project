# 🧠 AI-Powered Meeting Intelligence System Using NLP

[![Python](https://img.shields.io/badge/Python-3.11+-3776ab?logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.x-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![NLTK](https://img.shields.io/badge/NLTK-NLP-green)](https://www.nltk.org)
[![Deploy on Render](https://img.shields.io/badge/Render-Deploy-46E3B7?logo=render&logoColor=white)](https://render.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A smart meeting transcript analyzer that uses Natural Language Processing to extract actionable insights from your meetings. Paste or upload a transcript and get an instant, comprehensive meeting report.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📝 **Extractive Summarization** | Weighted sentence scoring with position & keyword boosts |
| 🏷️ **Topic Extraction** | Identifies key discussion topics via TF analysis |
| ☁️ **Word Cloud** | Visual word-frequency cloud rendered in the browser |
| 🎯 **Action Items + Priority** | Detects tasks, owners, deadlines, and classifies priority (High / Medium / Low) |
| 📌 **Decision Detection** | Finds decision statements using expanded keyword cues |
| 😊 **Sentiment Analysis** | Overall + per-speaker sentiment via VADER (NLTK) |
| 👥 **Speaker Statistics** | Word count, participation %, and contribution bars per speaker |
| ❓ **Question Detection** | Extracts questions raised during the meeting |
| 👤 **Entity Recognition** | Detects people & dates (spaCy NER or regex fallback) |
| ⏱️ **Duration Estimate** | Rough meeting length based on word count |
| 🌙 **Dark / Light Theme** | Toggle with preference saved in localStorage |
| 📋 **Analysis History** | Past analyses saved in browser for quick access |
| 📄 **Report Download** | Download a formatted TXT report |
| 📋 **Copy Summary** | One-click copy to clipboard |
| 📝 **Sample Transcripts** | Built-in sample meetings for quick demo |
| 📁 **File Upload** | Upload `.txt` transcript files |
| 🚀 **Deploy-Ready** | Render.com blueprint with Gunicorn |

---

## 🖥️ Screenshots

### Light Theme
> Analyze transcripts with a clean, modern interface featuring tabbed results.

### Dark Theme
> Full dark mode support with automatic preference saving.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.11+, Flask 3.x
- **NLP**: NLTK (VADER sentiment), spaCy (optional NER), regex patterns
- **Frontend**: Vanilla HTML5, CSS3, JavaScript (ES6+)
- **Deployment**: Gunicorn, Render.com

---

## 🚀 Quick Start (Local)

### Prerequisites
- Python 3.11 or 3.12

### Setup

```bash
# 1. Clone the repository
git clone https://github.com/AsrithaAmbure/NLP_minor_project.git
cd NLP_minor_project

# 2. Create virtual environment
python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# Windows CMD
.venv\Scripts\activate.bat
# macOS / Linux
source .venv/bin/activate

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. (Optional) Install spaCy model for better entity recognition
pip install spacy>=3.7
python -m spacy download en_core_web_sm

# 5. Run the app
python app.py
```

Open **http://127.0.0.1:5000** in your browser.

---

## 🌐 Deploy to Render (Free)

This project includes a `render.yaml` blueprint for one-click deployment.

1. Push the code to your GitHub repository.
2. Go to [Render Dashboard](https://dashboard.render.com) → **New** → **Blueprint**.
3. Connect your GitHub repo.
4. Render will auto-detect `render.yaml` and deploy.
5. Your app will be live at `https://meeting-intelligence.onrender.com` (or similar).

### Manual Deployment

1. Create a new **Web Service** on Render.
2. Connect your GitHub repo.
3. Set:
   - **Build Command**: `pip install -r requirements.txt && python -c "import nltk; nltk.download('vader_lexicon', quiet=True)"`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120`
4. Deploy!

---

## 📁 Project Structure

```
NLP_minor_project/
├── app.py                 # Flask application & API routes
├── nlp_utils.py           # NLP analysis pipeline
├── requirements.txt       # Python dependencies
├── Procfile               # Gunicorn process file
├── render.yaml            # Render deployment blueprint
├── .gitignore             # Git ignore rules
├── README.md              # This file
├── templates/
│   └── index.html         # Main UI template
└── static/
    ├── style.css           # Stylesheet (light + dark themes)
    └── script.js           # Frontend logic (AJAX, tabs, history)
```

---

## 🔌 API Reference

### `POST /api/analyze`

Analyze a meeting transcript.

**Request (JSON):**
```json
{
  "transcript": "Ravi: We need to finish by November 10..."
}
```

**Response:**
```json
{
  "summary": "...",
  "topics": ["project", "frontend", ...],
  "decisions": ["We agreed to ..."],
  "actions": [
    {"task": "...", "owner": "Priya", "deadline": "November 5", "priority": "Medium"}
  ],
  "sentiment": {"label": "Positive", "emoji": "😊", "compound": 0.42, ...},
  "speaker_stats": [{"speaker": "Ravi", "word_count": 85, "percentage": 35.2}],
  "speaker_sentiment": [{"speaker": "Ravi", "sentiment": "Positive", "score": 0.3}],
  "questions": [{"question": "Should we update docs?", "speaker": "Priya"}],
  "word_cloud": [{"text": "project", "count": 5, "size": 100}],
  "people": ["Ravi", "Priya"],
  "dates": ["November 10"],
  "duration": "~2 min",
  "word_count": 245
}
```

### `POST /api/download/txt`

Download a formatted TXT report.

### `GET /health`

Health check endpoint (returns `{"status": "healthy"}`).

---

## 📝 Sample Transcript

```
Ravi: Good morning everyone. Let's start with the sprint update.
Priya: I completed the user authentication module yesterday.
Priya: I will start working on the dashboard by tomorrow.
Arun: The database migration is still in progress.
Ravi: Sure, I will review the schema by end of day.
Ravi: We agreed to prioritize the API integration for this sprint.
Priya: I will test the login page before November 8.
Arun: I will fix the password reset bug today. It's a critical blocker.
Ravi: We decided to move the release date to November 15.
```

---

## 🧪 How It Works

| Module | Technique |
|--------|-----------|
| **Summarization** | Extractive — TF-based sentence scoring with position & keyword boosts |
| **Topics** | Word frequency analysis minus stopwords |
| **Sentiment** | VADER lexicon (NLTK) with keyword fallback |
| **Action Items** | Regex patterns matching "X will…", "X should…", etc. |
| **Priority** | Keyword classification (urgent/critical → High, optional → Low) |
| **Decisions** | Cue-phrase matching ("we decided", "agreed", "approved", etc.) |
| **Speakers** | Regex parsing of "Name: dialogue" format |
| **Questions** | Direct ("?") + indirect phrase detection |
| **Entities** | spaCy NER (PERSON, DATE) or regex fallback |

---

## ⚠️ Limitations

- This is a **student mini-project**, not a production meeting assistant.
- Action items and decisions are extracted using **pattern matching** — some will be missed.
- Speaker identification requires the `Name: dialogue` format.
- The "I will…" owner is inferred only when a speaker label precedes it.
- Dates are not always correctly linked to tasks.
- **Always verify** results against the original transcript.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

<p align="center">
  Made with ❤️ for NLP Minor Project
</p>
