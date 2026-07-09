"""
Custom Dashboard (Task 3)
Shows lead pipeline, scores, and conversation history.
"""
from flask import Flask, render_template, jsonify
import db

app = Flask(__name__)


@app.route("/")
def dashboard():
    leads = db.get_all_leads()
    counts = {"Hot": 0, "Warm": 0, "Cold": 0, "Unqualified": 0}
    for lead in leads:
        counts[lead.get("score", "Unqualified")] = counts.get(lead.get("score", "Unqualified"), 0) + 1
    return render_template("dashboard.html", leads=leads, counts=counts)


@app.route("/api/leads")
def api_leads():
    return jsonify(db.get_all_leads())


@app.route("/api/messages/<chat_id>")
def api_messages(chat_id):
    return jsonify(db.get_messages(chat_id))


if __name__ == "__main__":
    db.init_db()
    app.run(debug=True, port=5000)
