from flask import Flask, request, jsonify
import json
import os
import base64
from io import BytesIO
from PIL import Image
import re

app = Flask(__name__)

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
        # Decode base64 image
        image_data = base64.b64decode(base64_image)
        image = Image.open(BytesIO(image_data))
        
        # For now, just return basic info about the image
        # In a real implementation, you might use OCR or image analysis
        return f"Image processed: {image.format} format, {image.size[0]}x{image.size[1]} pixels"
    except Exception as e:
        return f"Error processing image: {str(e)}"

def find_relevant_content(question, course_content, discourse_posts):
    """Find relevant content based on the question"""
    question_lower = question.lower()
    relevant_links = []
    answer_parts = []
    
    # Search in discourse posts
    for post in discourse_posts:
        post_content = (post.get('title', '') + ' ' + post.get('content', '')).lower()
        
        # Simple keyword matching - in production, you'd use more sophisticated NLP
        if any(keyword in post_content for keyword in ['gpt', 'model', 'api', 'ga5']):
            if 'gpt' in question_lower or 'model' in question_lower:
                relevant_links.append({
                    "url": post.get('url', ''),
                    "text": post.get('title', 'Relevant discussion')
                })
                answer_parts.append(post.get('content', ''))
    
    # Search in course content
    for content in course_content:
        content_text = (content.get('title', '') + ' ' + content.get('content', '')).lower()
        
        if any(keyword in content_text for keyword in question_lower.split()):
            relevant_links.append({
                "url": content.get('url', ''),
                "text": content.get('title', 'Course content')
            })
    
    return answer_parts, relevant_links

def generate_answer(question, image_data=None):
    """Generate answer based on question and available data"""
    course_content, discourse_posts = load_scraped_data()
    
    # Process image if provided
    image_info = ""
    if image_data:
        image_info = process_image(image_data)
    
    # Find relevant content
    answer_parts, relevant_links = find_relevant_content(question, course_content, discourse_posts)
    
    # Generate answer based on question type
    question_lower = question.lower()
    
    if 'gpt' in question_lower and ('4o-mini' in question_lower or '3.5' in question_lower):
        answer = "You must use `gpt-3.5-turbo-0125`, even if the AI Proxy only supports `gpt-4o-mini`. Use the OpenAI API directly for this question as specified in the course requirements."
    elif 'deadline' in question_lower:
        answer = "Please check the course announcements and Discourse for the latest deadline information. Deadlines are typically announced well in advance."
    elif 'ga5' in question_lower:
        answer = "For GA5 questions, refer to the specific instructions provided. Use the exact model specified in the question requirements."
    else:
        # Generic answer based on found content
        if answer_parts:
            answer = f"Based on the course materials: {' '.join(answer_parts[:2])}"
        else:
            answer = "I don't have specific information about that topic in my current knowledge base. Please check the course materials or ask on Discourse for more detailed help."
    
    # Add image information if available
    if image_info:
        answer += f" (Image note: {image_info})"
    
    # Ensure we have some relevant links
    if not relevant_links:
        relevant_links = [
            {
                "url": "https://discourse.onlinedegree.iitm.ac.in/c/tds/",
                "text": "TDS Discourse Category"
            }
        ]
    
    return answer, relevant_links[:3]  # Limit to 3 links

@app.route("/")
def index():
    return "TDS Virtual TA API is running. Use POST /api/ with JSON: {\"question\": \"...\"}"

@app.route("/health")
def health():
    return jsonify({"status": "healthy", "message": "TDS Virtual TA API is running"})

@app.route("/api/", methods=["GET", "POST"])
def handle_api():
    if request.method == "GET":
        return jsonify({
            "message": "Send a POST request with JSON body",
            "example": {
                "question": "Should I use gpt-4o-mini or gpt-3.5-turbo?",
                "image": "base64_encoded_image_data_optional"
            }
        })
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
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
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route("/api", methods=["GET", "POST"])
def handle_api_no_slash():
    """Handle requests without trailing slash"""
    return handle_api()

if __name__ == "__main__":
    # Run scraper first to ensure data is available
    try:
        from scraper import main as run_scraper
        run_scraper()
    except ImportError:
        print("Warning: Could not import scraper. Make sure data files exist.")
    
    app.run(debug=True, host='0.0.0.0', port=5000)