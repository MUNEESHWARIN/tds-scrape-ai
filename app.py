from flask import Flask, request, jsonify
from scraper import scrape_content

app = Flask(__name__)

@app.route("/")
def index():
    return "Welcome to the Scraper API. Use POST /api/ with JSON: {\"question\": \"...\"}"

@app.route("/api/", methods=["GET", "POST"])
def handle_scrape():
    if request.method == "GET":
        return jsonify({
            "message": "Send a POST request with JSON body: {\"question\": \"your question here\"}"
        })
    
    try:
        data = request.get_json()
        question = data.get("question", "")
        if not question:
            return jsonify({"error": "No question provided"}), 400
        result = scrape_content(question)
        return jsonify({"answer": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
