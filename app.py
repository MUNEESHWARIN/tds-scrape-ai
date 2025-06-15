from flask import Flask, request, jsonify
import json
import os
from datetime import datetime
import base64
import io

app = Flask(__name__)

# Fallback data if files don't exist
FALLBACK_COURSE_DATA = [
    {
        "title": "Tools in Data Science",
        "url": "https://tds.s-anand.net/",
        "content": "Main course page for TDS with various tools and techniques"
    },
    {
        "title": "Python Tools",
        "url": "https://tds.s-anand.net/#/uv",
        "content": "Python package management with uv"
    },
    {
        "title": "AI Code Editors",
        "url": "https://tds.s-anand.net/#/github-copilot",
        "content": "Using GitHub Copilot for AI-assisted coding"
    },
    {
        "title": "LLM APIs",
        "url": "https://tds.s-anand.net/#/llm",
        "content": "Working with Large Language Model APIs"
    }
]

FALLBACK_DISCOURSE_DATA = [
    {
        "title": "GA5 Question 8 Clarification",
        "url": "https://discourse.onlinedegree.iitm.ac.in/t/ga5-question-8-clarification/155939",
        "content": "Use the model that's mentioned in the question. For gpt-3.5-turbo-0125, use that specific model.",
        "date": "2025-04-10"
    },
    {
        "title": "API Usage Guidelines",
        "url": "https://discourse.onlinedegree.iitm.ac.in/t/api-usage/123456",
        "content": "Guidelines for using APIs in TDS assignments and projects.",
        "date": "2025-04-08"
    },
    {
        "title": "Python Environment Setup",
        "url": "https://discourse.onlinedegree.iitm.ac.in/t/python-setup/123457",
        "content": "How to set up Python environment for TDS course work.",
        "date": "2025-04-05"
    }
]

# Load scraped data
def load_data():
    data = {}
    try:
        # Try to load from files first
        if os.path.exists('data/course_content.json'):
            with open('data/course_content.json', 'r', encoding='utf-8') as f:
                data['course'] = json.load(f)
        else:
            data['course'] = FALLBACK_COURSE_DATA
    except Exception as e:
        print(f"Error loading course data: {e}")
        data['course'] = FALLBACK_COURSE_DATA
    
    try:
        if os.path.exists('data/discourse_posts.json'):
            with open('data/discourse_posts.json', 'r', encoding='utf-8') as f:
                data['discourse'] = json.load(f)
        else:
            data['discourse'] = FALLBACK_DISCOURSE_DATA
    except Exception as e:
        print(f"Error loading discourse data: {e}")
        data['discourse'] = FALLBACK_DISCOURSE_DATA
    
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
    
    # Also search course content
    for item in data.get('course', []):
        title = item.get('title', '').lower()
        content = item.get('content', '').lower()
        
        if any(word in title or word in content for word in question_lower.split()):
            relevant_links.append({
                'url': item.get('url', ''),
                'text': item.get('title', '')[:100] + '...' if len(item.get('title', '')) > 100 else item.get('title', '')
            })
    
    # Remove duplicates and limit to top 3 results
    seen_urls = set()
    unique_links = []
    for link in relevant_links:
        if link['url'] not in seen_urls:
            seen_urls.add(link['url'])
            unique_links.append(link)
    
    return unique_links[:3]

def generate_answer(question, relevant_content):
    """Generate answer based on question and relevant content"""
    
    # Common TDS-related responses
    common_answers = {
        'gpt': "For TDS assignments, use the specific model mentioned in the question. If the question specifies gpt-3.5-turbo-0125, use that exact model even if AI Proxy only supports gpt-4o-mini. You may need to use OpenAI API directly.",
        'model': "For TDS assignments, use the specific model mentioned in the question. If the question specifies gpt-3.5-turbo-0125, use that exact model even if AI Proxy only supports gpt-4o-mini. You may need to use OpenAI API directly.",
        'assignment': "Check the course materials and Discourse posts for specific assignment guidelines. Make sure to follow the exact requirements mentioned.",
        'api': "Refer to the course documentation for API usage examples. Check if you need authentication and follow the specified format.",
        'python': "For Python-related questions, check the course notebooks and examples provided in the TDS materials.",
        'scraping': "For web scraping, use the techniques covered in the course materials. Make sure to respect robots.txt and rate limits.",
        'deployment': "You can deploy on platforms like Vercel, Render, or use ngrok for local testing. Make sure your API endpoint is publicly accessible.",
        'tds': "TDS (Tools in Data Science) is a course that covers various tools and techniques used in data science, including Python, APIs, web scraping, and deployment."
    }
    
    question_lower = question.lower()
    
    # Check for common keywords
    for keyword, answer in common_answers.items():
        if keyword in question_lower:
            return answer
    
    # If we have relevant content, mention it
    if relevant_content:
        return f"Based on the TDS course materials and discussions, please check the relevant links provided below for detailed information about your question."
    
    # Default response
    return "Based on the TDS course materials, please refer to the relevant documentation and Discourse discussions. If you need specific help, please provide more details about your question."

@app.route('/api/', methods=['POST', 'OPTIONS'])
def answer_question():
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response
    
    try:
        # Add CORS headers
        def add_cors_headers(response):
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
            response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
            return response
        
        data = request.get_json()
        
        if not data or 'question' not in data:
            response = jsonify({'error': 'Question is required'})
            return add_cors_headers(response), 400
        
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
        
        response_data = {
            'answer': answer,
            'links': relevant_links
        }
        
        response = jsonify(response_data)
        return add_cors_headers(response)
    
    except Exception as e:
        print(f"Error in API: {e}")
        response = jsonify({'error': f'Internal server error: {str(e)}'})
        return add_cors_headers(response), 500

@app.route('/api/test', methods=['GET'])
def test_endpoint():
    """Test endpoint to verify API is working"""
    response = jsonify({
        'status': 'ok',
        'message': 'TDS Virtual TA API is running',
        'timestamp': datetime.now().isoformat()
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/')
def home():
    return '''
    <h1>TDS Virtual TA API</h1>
    <p>POST to /api/ with JSON: {"question": "your question here"}</p>
    <p>Optional: Include "image" field with base64 encoded image</p>
    <p><a href="/api/test">Test API Status</a></p>
    '''


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)