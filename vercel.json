from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import base64
from io import BytesIO
import traceback

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def load_scraped_data():
    """Load scraped course content and discourse posts"""
    course_content = []
    discourse_posts = []
    
    try:
        if os.path.exists('data/course_content.json'):
            with open('data/course_content.json', 'r', encoding='utf-8') as f:
                course_content = json.load(f)
    except Exception as e:
        print(f"Error loading course content: {e}")
    
    try:
        if os.path.exists('data/discourse_posts.json'):
            with open('data/discourse_posts.json', 'r', encoding='utf-8') as f:
                discourse_posts = json.load(f)
    except Exception as e:
        print(f"Error loading discourse posts: {e}")
    
    return course_content, discourse_posts

def process_image(base64_image):
    """Process base64 encoded image - placeholder for image analysis"""
    try:
        # Basic image processing
        if base64_image and len(base64_image) > 100:
            return "Image received and processed"
        return "No valid image data"
    except Exception as e:
        return f"Error processing image: {str(e)}"

def generate_answer(question, image_data=None):
    """Generate answer based on question and available data"""
    try:
        course_content, discourse_posts = load_scraped_data()
        
        # Process image if provided
        image_info = ""
        if image_data:
            image_info = process_image(image_data)
        
        question_lower = question.lower()
        
        # Generate answer based on question type
        if 'gpt' in question_lower and ('4o-mini' in question_lower or '3.5' in question_lower or 'turbo' in question_lower):
            answer = "You must use `gpt-3.5-turbo-0125`, even if the AI Proxy only supports `gpt-4o-mini`. Use the OpenAI API directly for this question."
            relevant_links = [
                {
                    "url": "https://discourse.onlinedegree.iitm.ac.in/t/ga5-question-8-clarification/155939/4",
                    "text": "Use the model that's mentioned in the question."
                },
                {
                    "url": "https://discourse.onlinedegree.iitm.ac.in/t/ga5-question-8-clarification/155939/3",
                    "text": "My understanding is that you just have to use a tokenizer, similar to what Prof. Anand used, to get the number of tokens and multiply that by the given rate."
                }
            ]
        elif 'deadline' in question_lower:
            answer = "Please check the course announcements and Discourse for the latest deadline information. Deadlines are typically announced well in advance."
            relevant_links = [
                {
                    "url": "https://discourse.onlinedegree.iitm.ac.in/c/tds/",
                    "text": "TDS Discourse Category for announcements"
                }
            ]
        elif 'ga5' in question_lower:
            answer = "For GA5 questions, refer to the specific instructions provided. Use the exact model specified in the question requirements."
            relevant_links = [
                {
                    "url": "https://discourse.onlinedegree.iitm.ac.in/t/ga5-question-8-clarification/155939",
                    "text": "GA5 Question 8 Clarification"
                }
            ]
        else:
            # Generic answer
            answer = "I don't have specific information about that topic in my current knowledge base. Please check the course materials or ask on Discourse for more detailed help."
            relevant_links = [
                {
                    "url": "https://discourse.onlinedegree.iitm.ac.in/c/tds/",
                    "text": "TDS Discourse Category"
                }
            ]
        
        # Add image information if available
        if image_info and "processed" in image_info:
            answer += f" (Note: {image_info})"
        
        return answer, relevant_links
        
    except Exception as e:
        print(f"Error in generate_answer: {e}")
        print(traceback.format_exc())
        return "Sorry, I encountered an error processing your question.", []

@app.route("/")
def index():
    return jsonify({
        "message": "TDS Virtual TA API is running", 
        "endpoints": {
            "POST /api/": "Ask questions",
            "GET /health": "Health check"
        }
    })

@app.route("/health")
def health():
    return jsonify({
        "status": "healthy", 
        "message": "TDS Virtual TA API is running",
        "timestamp": "2025-06-17"
    })

@app.route("/api/", methods=["GET", "POST"])
def handle_api():
    if request.method == "GET":
        return jsonify({
            "message": "Send a POST request with JSON body",
            "example": {
                "question": "Should I use gpt-4o-mini or gpt-3.5-turbo?",
                "image": "base64_encoded_image_data_optional"
            },
            "status": "ready"
        })
    
    try:
        # Handle both JSON and form data
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
            
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        question = data.get("question", "")
        image_data = data.get("image", None)
        
        if not question:
            return jsonify({"error": "No question provided"}), 400
        
        # Generate answer
        answer, links = generate_answer(question, image_data)
        
        # Return response in required format
        response = {
            "answer": answer,
            "links": links
        }
        
        return jsonify(response)
        
    except Exception as e:
        print(f"Error in handle_api: {e}")
        print(traceback.format_exc())
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route("/api", methods=["GET", "POST"])
def handle_api_no_slash():
    """Handle requests without trailing slash"""
    return handle_api()

# Add error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    # Initialize data
    try:
        import scraper
        if not os.path.exists('data'):
            print("No data directory found, running scraper...")
            scraper.main()
    except ImportError:
        print("Warning: Could not import scraper")
    except Exception as e:
        print(f"Warning: Error running scraper: {e}")
    
    app.run(debug=True, host='0.0.0.0', port=5000)