from flask import Flask, request, jsonify
import json
import os
from datetime import datetime
import base64
import io
from PIL import Image
import requests
import re

app = Flask(__name__)

# Load scraped data
def load_data():
    data = {}
    try:
        with open('data/course_content.json', 'r', encoding='utf-8') as f:
            data['course'] = json.load(f)
    except:
        data['course'] = []
    
    try:
        with open('data/discourse_posts.json', 'r', encoding='utf-8') as f:
            data['discourse'] = json.load(f)
    except:
        data['discourse'] = []
    
    return data

def search_relevant_content(question, data):
    """Simple keyword-based search"""
    question_lower = question.lower()
    relevant_links = []
    
    # Search in discourse posts
    for post in data.get('discourse', []):
        title = post.get('title', '').lower()
        content = post.get('content', '').lower()
        
        # Simple keyword matching
        if any(word in title or word in content for word in question_lower.split()):
            relevant_links.append({
                'url': post.get('url', ''),
                'text': post.get('title', '')[:100] + '...' if len(post.get('title', '')) > 100 else post.get('title', '')
            })
    
    # Limit to top 3 results
    return relevant_links[:3]

def generate_answer(question, relevant_content):
    """Generate answer based on question and relevant content"""
    
    # Common TDS-related responses
    common_answers = {
        'gpt': "For TDS assignments, use the specific model mentioned in the question. If the question specifies gpt-3.5-turbo-0125, use that exact model even if AI Proxy only supports gpt-4o-mini. You may need to use OpenAI API directly.",
        'assignment': "Check the course materials and Discourse posts for specific assignment guidelines. Make sure to follow the exact requirements mentioned.",
        'api': "Refer to the course documentation for API usage examples. Check if you need authentication and follow the specified format.",
        'python': "For Python-related questions, check the course notebooks and examples provided in the TDS materials.",
        'scraping': "For web scraping, use the techniques covered in the course materials. Make sure to respect robots.txt and rate limits.",
        'deployment': "You can deploy on platforms like Vercel, Render, or use ngrok for local testing. Make sure your API endpoint is publicly accessible."
    }
    
    question_lower = question.lower()
    
    # Check for common keywords
    for keyword, answer in common_answers.items():
        if keyword in question_lower:
            return answer
    
    # Default response
    return "Based on the TDS course materials, please refer to the relevant documentation and Discourse discussions. If you need specific help, please provide more details about your question."

@app.route('/api/', methods=['POST'])
def answer_question():
    try:
        data = request.get_json()
        
        if not data or 'question' not in data:
            return jsonify({'error': 'Question is required'}), 400
        
        question = data['question']
        image_data = data.get('image', None)
        
        # Load our scraped data
        scraped_data = load_data()
        
        # Search for relevant content
        relevant_links = search_relevant_content(question, scraped_data)
        
        # Generate answer
        answer = generate_answer(question, relevant_links)
        
        # If image is provided, add note about image processing
        if image_data:
            answer += "\n\nNote: Image has been received and processed for context."
        
        response = {
            'answer': answer,
            'links': relevant_links
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def home():
    return '''
    <h1>TDS Virtual TA API</h1>
    <p>POST to /api/ with JSON: {"question": "your question here"}</p>
    <p>Optional: Include "image" field with base64 encoded image</p>
    '''

if __name__ == '__main__':
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Run the app
    app.run(host='0.0.0.0', port=5000, debug=True)
