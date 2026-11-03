"""
NLP Utilities for Meeting Intelligence System
──────────────────────────────────────────────
Provides: summarization, topic extraction, sentiment analysis,
speaker statistics, question detection, action-item extraction
with priority classification, entity recognition, and word-cloud data.
"""

import re
from collections import Counter, defaultdict

# ─── VADER Sentiment (NLTK) ───────────────────────────────
try:
    import nltk
    from nltk.sentiment.vader import SentimentIntensityAnalyzer

    try:
        nltk.data.find("sentiment/vader_lexicon.zip")
    except LookupError:
        nltk.download("vader_lexicon", quiet=True)
    VADER = SentimentIntensityAnalyzer()
except Exception:
    VADER = None

# ─── Optional spaCy ───────────────────────────────────────
try:
    import spacy

    try:
        NLP = spacy.load("en_core_web_sm")
    except OSError:
        NLP = None
except ImportError:
    NLP = None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  SHARED STOPWORDS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STOPWORDS = frozenset({
    "the", "a", "an", "and", "or", "but", "to", "of", "in", "on", "for",
    "is", "are", "was", "were", "we", "i", "you", "it", "this", "that",
    "will", "be", "by", "with", "as", "at", "from", "our", "they", "he",
    "she", "their", "have", "has", "had", "do", "does", "did", "about",
    "need", "needs", "going", "okay", "please", "think", "know", "just",
    "like", "can", "also", "would", "could", "should", "get", "got",
    "make", "made", "said", "let", "us", "its", "all", "so", "if",
    "been", "being", "not", "no", "yes", "there", "here", "when",
    "what", "how", "who", "which", "than", "then", "them", "these",
    "those", "each", "every", "any", "some", "more", "most", "other",
    "into", "over", "such", "up", "out", "very", "only", "own",
    "don", "didn", "doesn", "won", "wouldn", "couldn", "shouldn",
    "want", "wanted", "tell", "told", "say", "says", "really",
})


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  SENTENCE SPLITTING
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def split_sentences(text):
    """Split text into sentences."""
    cleaned = re.sub(r"\s+", " ", text).strip()
    if not cleaned:
        return []
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", cleaned) if s.strip()]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  SUMMARIZATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def extractive_summary(text, max_sentences=4):
    """Weighted extractive summary with position and keyword boosts."""
    sentences = split_sentences(text)
    if len(sentences) <= max_sentences:
        return " ".join(sentences)

    words = re.findall(r"\b[a-zA-Z][a-zA-Z'-]*\b", text.lower())
    freq = Counter(w for w in words if w not in STOPWORDS and len(w) > 2)

    boost_keywords = {
        "decided", "agreed", "will", "deadline", "important", "priority",
        "approved", "conclusion", "summary", "result", "action", "completed",
        "urgent", "critical", "finalized", "assigned",
    }

    scored = []
    for idx, sent in enumerate(sentences):
        tokens = re.findall(r"\b[a-zA-Z][a-zA-Z'-]*\b", sent.lower())
        base = sum(freq[t] for t in tokens if t not in STOPWORDS)
        pos_boost = 1.2 if idx == 0 or idx == len(sentences) - 1 else 1.0
        kw_boost = 1.3 if any(kw in sent.lower() for kw in boost_keywords) else 1.0
        score = (base / max(len(tokens), 1)) * pos_boost * kw_boost
        scored.append((score, idx, sent))

    top = sorted(sorted(scored, reverse=True)[:max_sentences], key=lambda x: x[1])
    return " ".join(item[2] for item in top)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  SENTIMENT ANALYSIS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
_POS_WORDS = frozenset({
    "good", "great", "excellent", "agree", "approved", "happy", "success",
    "progress", "completed", "well", "fantastic", "wonderful", "perfect",
    "yes", "love", "best", "exciting", "positive", "productive",
})
_NEG_WORDS = frozenset({
    "bad", "problem", "issue", "delay", "failed", "concern", "risk",
    "difficult", "wrong", "worry", "behind", "miss", "missing", "late",
    "bug", "error", "disagree", "blocker", "stuck", "negative",
})


def analyze_sentiment(text):
    """Overall sentiment of the text using VADER or keyword fallback."""
    if VADER:
        scores = VADER.polarity_scores(text)
        c = scores["compound"]
        if c >= 0.05:
            label, emoji = "Positive", "😊"
        elif c <= -0.05:
            label, emoji = "Negative", "😟"
        else:
            label, emoji = "Neutral", "😐"
        return {
            "label": label, "emoji": emoji,
            "compound": round(c, 3),
            "positive": round(scores["pos"], 3),
            "negative": round(scores["neg"], 3),
            "neutral": round(scores["neu"], 3),
        }

    # Keyword fallback
    tokens = set(re.findall(r"\b[a-z]+\b", text.lower()))
    pos = len(tokens & _POS_WORDS)
    neg = len(tokens & _NEG_WORDS)
    total = pos + neg or 1
    compound = round((pos - neg) / total, 3)
    if compound > 0.1:
        label, emoji = "Positive", "😊"
    elif compound < -0.1:
        label, emoji = "Negative", "😟"
    else:
        label, emoji = "Neutral", "😐"
    return {
        "label": label, "emoji": emoji, "compound": compound,
        "positive": round(pos / total, 3),
        "negative": round(neg / total, 3),
        "neutral": round(max(0, 1 - (pos + neg) / max(len(tokens), 1)), 3),
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  SPEAKER PARSING & STATS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def parse_speakers(text):
    """Parse speaker-labelled text ('Name: dialogue')."""
    speakers = defaultdict(list)
    for m in re.finditer(
        r"(?:^|\n)\s*([A-Z][A-Za-z'-]+)\s*:\s*(.+?)(?=\n\s*[A-Z][A-Za-z'-]+\s*:|$)",
        text, re.DOTALL,
    ):
        name = m.group(1).strip()
        dialogue = m.group(2).strip()
        if dialogue:
            speakers[name].append(dialogue)
    return dict(speakers)


def get_speaker_stats(text):
    """Word count and participation percentage per speaker."""
    speakers = parse_speakers(text)
    if not speakers:
        return []
    stats = []
    total_words = 0
    for speaker, lines in speakers.items():
        wc = sum(len(line.split()) for line in lines)
        total_words += wc
        stats.append({"speaker": speaker, "word_count": wc, "line_count": len(lines)})
    for s in stats:
        s["percentage"] = round((s["word_count"] / max(total_words, 1)) * 100, 1)
    return sorted(stats, key=lambda x: x["word_count"], reverse=True)


def analyze_speaker_sentiment(text):
    """Per-speaker sentiment."""
    speakers = parse_speakers(text)
    if not speakers:
        return []
    results = []
    for speaker, lines in speakers.items():
        combined = " ".join(lines)
        s = analyze_sentiment(combined)
        results.append({
            "speaker": speaker,
            "sentiment": s["label"],
            "emoji": s["emoji"],
            "score": s["compound"],
        })
    return sorted(results, key=lambda x: x["score"], reverse=True)


def estimate_duration(text):
    """Rough duration estimate (~130 words / min in a meeting)."""
    wc = len(text.split())
    mins = max(1, round(wc / 130))
    if mins < 60:
        return f"~{mins} min"
    h, m = divmod(mins, 60)
    return f"~{h}h {m}m" if m else f"~{h}h"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ENTITY RECOGNITION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def get_entities(text):
    """Extract people and dates from text."""
    people, dates = [], []
    if NLP:
        doc = NLP(text[:100_000])
        people = list(dict.fromkeys(
            e.text for e in doc.ents if e.label_ == "PERSON"))
        dates = list(dict.fromkeys(
            e.text for e in doc.ents if e.label_ in {"DATE", "TIME"}))
    else:
        people = list(parse_speakers(text).keys())
        dates = list(dict.fromkeys(re.findall(
            r"\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|"
            r"Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|"
            r"Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2}(?:,\s*\d{4})?\b|"
            r"\b\d{1,2}/\d{1,2}/\d{2,4}\b",
            text, flags=re.IGNORECASE,
        )))
    return people, dates


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  QUESTION DETECTION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
_INDIRECT_Q = frozenset({
    "wondering if", "any thoughts on", "what do you think",
    "can someone", "does anyone", "should we", "shall we",
    "how about", "what about", "any ideas",
})


def extract_questions(text):
    """Return questions (direct and indirect) with speaker attribution."""
    questions = []
    for sent in split_sentences(text):
        is_q = sent.strip().endswith("?") or any(p in sent.lower() for p in _INDIRECT_Q)
        if not is_q:
            continue
        sp = re.match(r"^\s*([A-Z][A-Za-z'-]+)\s*:", sent)
        cleaned = re.sub(r"^\s*[A-Z][A-Za-z'-]+\s*:\s*", "", sent).strip()
        questions.append({
            "question": cleaned,
            "speaker": sp.group(1) if sp else "Unknown",
        })
    return questions[:12]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ACTION ITEMS WITH PRIORITY
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ACTION_PATTERNS = [
    r"\bI will (?P<task>[^.!?]+)",
    r"\b(?P<owner>[A-Z][a-z]+) will (?P<task>[^.!?]+)",
    r"\b(?P<owner>[A-Z][a-z]+) is responsible for (?P<task>[^.!?]+)",
    r"\b(?P<owner>[A-Z][a-z]+) should (?P<task>[^.!?]+)",
    r"\b(?P<owner>[A-Z][a-z]+) needs to (?P<task>[^.!?]+)",
    r"\b(?P<owner>[A-Z][a-z]+) must (?P<task>[^.!?]+)",
    r"\b(?P<owner>[A-Z][a-z]+) has to (?P<task>[^.!?]+)",
    r"\bAction item:\s*(?P<task>[^.!?]+)",
    r"\bAssign(?:ed)? to (?P<owner>[A-Z][a-z]+):\s*(?P<task>[^.!?]+)",
    r"\bTODO:\s*(?P<task>[^.!?]+)",
]

_HIGH_KW = frozenset({
    "urgent", "asap", "immediately", "critical", "blocker", "today",
    "deadline", "must", "emergency", "high priority", "crucial",
})
_LOW_KW = frozenset({
    "eventually", "when possible", "nice to have", "low priority",
    "whenever", "someday", "optional", "consider",
})


def _classify_priority(task, sentence):
    combo = (task + " " + sentence).lower()
    if any(kw in combo for kw in _HIGH_KW):
        return "High"
    if any(kw in combo for kw in _LOW_KW):
        return "Low"
    if re.search(r"\b(?:today|tomorrow|by end of day|by eod)\b", combo):
        return "High"
    return "Medium"


def extract_actions(text):
    """Rule-based task extraction with priority classification."""
    actions = []
    for sentence in split_sentences(text):
        for pattern in ACTION_PATTERNS:
            match = re.search(pattern, sentence, flags=re.IGNORECASE)
            if not match:
                continue
            task = match.groupdict().get("task", "").strip(" ,;:")
            owner = match.groupdict().get("owner") or "Not specified"

            sp = re.match(r"^\s*([A-Z][A-Za-z'-]+)\s*:\s*", sentence)
            if owner == "Not specified" and sp:
                owner = sp.group(1)

            task = re.sub(r"^[A-Z][A-Za-z'-]+\s*:\s*", "", task).strip()
            if not task:
                continue

            dm = re.search(
                r"\b(?:by|before|on|due(?:\s+by)?)\s+"
                r"((?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|"
                r"Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|"
                r"Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2}(?:,\s*\d{4})?|"
                r"\d{1,2}/\d{1,2}/\d{2,4})",
                sentence, flags=re.IGNORECASE,
            )
            item = {
                "task": task,
                "owner": owner,
                "deadline": dm.group(1) if dm else "Not specified",
                "priority": _classify_priority(task, sentence),
            }
            if item not in actions:
                actions.append(item)
            break
    return actions


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  DECISION EXTRACTION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
_DECISION_CUES = [
    "we decided", "we agreed", "decision:", "it was decided",
    "we will", "let's", "the team agreed", "approved",
    "consensus", "voted", "finalized", "concluded",
    "we're going with", "settled on", "agreed upon",
]


def extract_decisions(text):
    return [
        s for s in split_sentences(text)
        if any(c in s.lower() for c in _DECISION_CUES)
    ][:10]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  TOPIC & WORD-CLOUD DATA
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def extract_topics(text, limit=10):
    words = re.findall(r"\b[a-zA-Z][a-zA-Z'-]{2,}\b", text.lower())
    counts = Counter(w for w in words if w not in STOPWORDS)
    return [w for w, _ in counts.most_common(limit)]


def get_word_cloud_data(text, limit=30):
    """Word frequencies normalised to 0-100 for the front-end cloud."""
    words = re.findall(r"\b[a-zA-Z][a-zA-Z'-]{2,}\b", text.lower())
    counts = Counter(w for w in words if w not in STOPWORDS)
    top = counts.most_common(limit)
    if not top:
        return []
    mx = top[0][1]
    return [
        {"text": w, "count": c, "size": round((c / mx) * 100)}
        for w, c in top
    ]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  MAIN ANALYSIS ENTRY POINT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def analyze_meeting(text):
    """Run the complete analysis pipeline and return a dict."""
    people, dates = get_entities(text)
    return {
        "summary":            extractive_summary(text),
        "topics":             extract_topics(text),
        "decisions":          extract_decisions(text),
        "actions":            extract_actions(text),
        "people":             people,
        "dates":              dates,
        "sentiment":          analyze_sentiment(text),
        "speaker_sentiment":  analyze_speaker_sentiment(text),
        "speaker_stats":      get_speaker_stats(text),
        "questions":          extract_questions(text),
        "duration":           estimate_duration(text),
        "word_cloud":         get_word_cloud_data(text),
        "word_count":         len(text.split()),
        "transcript":         text,
    }
