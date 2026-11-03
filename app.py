"""
Meeting Intelligence — Flask Application
─────────────────────────────────────────
JSON API for the front-end + downloadable reports.
"""

from io import BytesIO
from flask import Flask, render_template, request, send_file, jsonify
from nlp_utils import analyze_meeting

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB


# ── Pages ──────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


# ── JSON API ───────────────────────────────────────────────
@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    """Analyze a meeting transcript and return JSON results."""
    transcript = ""

    if request.is_json:
        transcript = (request.get_json() or {}).get("transcript", "").strip()
    else:
        transcript = request.form.get("transcript", "").strip()
        uploaded = request.files.get("transcript_file")
        if uploaded and uploaded.filename:
            if not uploaded.filename.lower().endswith(".txt"):
                return jsonify({"error": "Please upload a .txt file."}), 400
            try:
                transcript = uploaded.read().decode("utf-8-sig").strip()
            except UnicodeDecodeError:
                return jsonify({"error": "File must be UTF-8 encoded."}), 400

    if len(transcript) < 20:
        return jsonify({
            "error": "Transcript too short — please provide at least 20 characters."
        }), 400

    return jsonify(analyze_meeting(transcript))


# ── TXT Download ───────────────────────────────────────────
@app.route("/api/download/txt", methods=["POST"])
def download_txt():
    data = request.get_json() or {}
    transcript = data.get("transcript", "").strip()
    if len(transcript) < 20:
        return "Transcript is missing or too short.", 400

    r = analyze_meeting(transcript)
    lines = [
        "=" * 50,
        "   AI-POWERED MEETING INTELLIGENCE REPORT",
        "=" * 50,
        "",
        f"  Estimated Duration : {r['duration']}",
        f"  Word Count         : {r['word_count']}",
        f"  Overall Sentiment  : {r['sentiment']['label']}  "
        f"(score {r['sentiment']['compound']})",
        "",
        "-" * 50,
        "  MEETING SUMMARY",
        "-" * 50,
        r["summary"],
        "",
        "-" * 50,
        "  KEY TOPICS",
        "-" * 50,
        *[f"  * {t}" for t in r["topics"]],
        "",
        "-" * 50,
        "  KEY DECISIONS",
        "-" * 50,
    ]
    lines += [f"  * {d}" for d in r["decisions"]] or ["  (none detected)"]

    lines += ["", "-" * 50, "  ACTION ITEMS", "-" * 50]
    if r["actions"]:
        for a in r["actions"]:
            lines.append(
                f"  [{a['priority']}]  {a['task']}\n"
                f"          Owner: {a['owner']}  |  Deadline: {a['deadline']}"
            )
    else:
        lines.append("  (none detected)")

    if r["questions"]:
        lines += ["", "-" * 50, "  QUESTIONS RAISED", "-" * 50]
        for q in r["questions"]:
            lines.append(f"  [{q['speaker']}] {q['question']}")

    if r["speaker_stats"]:
        lines += ["", "-" * 50, "  SPEAKER STATISTICS", "-" * 50]
        for s in r["speaker_stats"]:
            bar = "#" * int(s["percentage"] / 5)
            lines.append(
                f"  {s['speaker']:15s} {bar:20s} "
                f"{s['percentage']}%  ({s['word_count']} words)"
            )

    lines += [
        "",
        "=" * 50,
        "  Note: Automatically extracted — verify against",
        "  the original transcript before relying on it.",
        "=" * 50,
    ]

    payload = "\n".join(lines).encode("utf-8")
    return send_file(
        BytesIO(payload),
        mimetype="text/plain; charset=utf-8",
        as_attachment=True,
        download_name="meeting_report.txt",
    )


# ── Health ─────────────────────────────────────────────────
@app.route("/health")
def health():
    return jsonify({"status": "healthy", "service": "meeting-intelligence"})


# ── Entry point ────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, port=5000)
