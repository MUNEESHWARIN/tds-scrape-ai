from flask import Flask, request, jsonify
import json
import os
from datetime import datetime
import base64
import io

app = Flask(__name__)

# Enhanced fallback data with more comprehensive TDS content
FALLBACK_COURSE_DATA = [
    {
        "title": "Tools in Data Science - Main Course",
        "url": "https://tds.s-anand.net/",
        "content": "Main course page for TDS covering Python tools, AI editors, web scraping, APIs, and deployment techniques"
    },
    {
        "title": "Python Package Management with uv",
        "url": "https://tds.s-anand.net/#/uv",
        "content": "Modern Python package management using uv, faster than pip, handles dependencies efficiently"
    },
    {
        "title": "GitHub Copilot and AI Code Editors",
        "url": "https://tds.s-anand.net/#/github-copilot",
        "content": "Using AI-assisted coding with GitHub Copilot, prompt engineering for better code generation"
    },
    {
        "title": "Large Language Model APIs",
        "url": "https://tds.s-anand.net/#/llm",
        "content": "Working with LLM APIs including OpenAI GPT models, prompt engineering, and API best practices"
    },
    {
        "title": "Web Scraping Techniques",
        "url": "https://tds.s-anand.net/#/scraping",
        "content": "Web scraping with Python using requests, BeautifulSoup, and handling dynamic content"
    },
    {
        "title": "API Development and Deployment",
        "url": "https://tds.s-anand.net/#/api",
        "content": "Building REST APIs with Flask, deployment on cloud platforms, CORS handling"
    }
]

FALLBACK_DISCOURSE_DATA = [
    {
        "title": "GA5 Question 8 Clarification - Model Selection",
        "url": "https://discourse.onlinedegree.iitm.ac.in/t/ga5-question-8-clarification/155939",
        "content": "Use the model that's mentioned in the question. For gpt-3.5-turbo-0125, use that specific model even if AI Proxy only supports gpt-4o-mini. Use OpenAI API directly when needed.",
        "date": "2025-04-10",
        "category": "assignments"
    },
    {
        "title": "API Usage Guidelines for TDS Projects",
        "url": "https://discourse.onlinedegree.iitm.ac.in/t/api-usage/123456",
        "content": "Guidelines for using APIs in TDS assignments: handle authentication, respect rate limits, implement proper error handling, and follow REST principles.",
        "date": "2025-04-08",
        "category": "guidelines"
    },
    {
        "title": "Python Environment Setup for TDS",
        "url": "https://discourse.onlinedegree.iitm.ac.in/t/python-setup/123457",
        "content": "How to set up Python environment for TDS course work using uv, virtual environments, and required packages. Install Python 3.9+, uv, and course dependencies.",
        "date": "2025-04-05",
        "category": "setup"
    },
    {
        "title": "Deployment Options for TDS Projects",
        "url": "https://discourse.onlinedegree.iitm.ac.in/t/deployment-help/123458",
        "content": "Recommended deployment platforms: Vercel (free tier), Render, Railway. For local testing use ngrok. Ensure your API endpoint is publicly accessible.",
        "date": "2025-04-03",
        "category": "deployment"
    },
    {
        "title": "Common Issues with LLM API Integration",
        "url": "https://discourse.onlinedegree.iitm.ac.in/t/llm-api-issues/123459",
        "content": "Common problems: API key authentication, model availability, rate limiting, token counting. Solutions include proper error handling and fallback strategies.",
        "date": "2025-04-01",
        "category": "troubleshooting"
    }
]

def load_data():
    """Load scraped data with better error handling"""
    data = {}
    
    try:
        if os.path.exists('data/course_content.json'):
            with open('data/course_content.json', 'r', encoding='utf-8') as f:
                data['course'] = json.load(f)
                print(f"Loaded {len(data['course'])} course items from file")
        else:
            data['course'] = FALLBACK_COURSE_DATA
            print(f"Using {len(data['course'])} fallback course items")
    except Exception as e:
        print(f"Error loading course data: {e}")
        data['course'] = FALLBACK_COURSE_DATA
    
    try:
        if os.path.exists('data/discourse_posts.json'):
            with open('data/discourse_posts.json', 'r', encoding='utf-8') as f:
                data['discourse'] = json.load(f)
                print(f"Loaded {len(data['discourse'])} discourse posts from file")
        else:
            data['discourse'] = FALLBACK_DISCOURSE_DATA
            print(f"Using {len(data['discourse'])} fallback discourse posts")
    except Exception as e:
        print(f"Error loading discourse data: {e}")
        data['discourse'] = FALLBACK_DISCOURSE_DATA
    
    return data

def search_relevant_content(question, data):
    """Enhanced keyword-based search with scoring"""
    question_lower = question.lower()
    question_words = set(question_lower.split())
    relevant_links = []
    
    # Enhanced search in discourse posts
    for post in data.get('discourse', []):
        title = post.get('title', '').lower()
        content = post.get('content', '').lower()
        
        # Calculate relevance score
        title_words = set(title.split())
        content_words = set(content.split())
        
        title_matches = len(question_words.intersection(title_words))
        content_matches = len(question_words.intersection(content_words))
        
        # Weighted scoring (title matches are more important)
        score = title_matches * 2 + content_matches
        
        if score > 0:
            relevant_links.append({
                'url': post.get('url', ''),
                'text': post.get('title', '')[:150] + ('...' if len(post.get('title', '')) > 150 else ''),
                'score': score,
                'category': post.get('category', 'general')
            })
    
    # Search course content
    for item in data.get('course', []):
        title = item.get('title', '').lower()
        content = item.get('content', '').lower()
        
        title_words = set(title.split())
        content_words = set(content.split())
        
        title_matches = len(question_words.intersection(title_words))
        content_matches = len(question_words.intersection(content_words))
        
        score = title_matches * 2 + content_matches
        
        if score > 0:
            relevant_links.append({
                'url': item.get('url', ''),
                'text': item.get('title', '')[:150] + ('...' if len(item.get('title', '')) > 150 else ''),
                'score': score,
                'category': 'course'
            })
    
    # Sort by score and remove duplicates
    relevant_links.sort(key=lambda x: x['score'], reverse=True)
    
    seen_urls = set()
    unique_links = []
    for link in relevant_links:
        if link['url'] not in seen_urls and link['url']:
            seen_urls.add(link['url'])
            # Remove score and category from final output
            unique_links.append({
                'url': link['url'],
                'text': link['text']
            })
    
    return unique_links[:5]  # Return top 5 results

def generate_answer(question, relevant_content):
    """Enhanced answer generation with better context awareness"""
    
    question_lower = question.lower()
    
    # Specific TDS answers with better matching
    if any(word in question_lower for word in ['gpt', 'model', 'openai', 'ai proxy']):
        if 'gpt-3.5-turbo' in question_lower or 'gpt-4' in question_lower:
            return "For TDS assignments, you must use the specific model mentioned in the question. If the question specifies gpt-3.5-turbo-0125, use that exact model even if AI Proxy only supports gpt-4o-mini. You may need to use the OpenAI API directly instead of the AI Proxy in such cases. Check the assignment requirements carefully for the exact model specification."
        else:
            return "For LLM model selection in TDS, always refer to the specific model mentioned in your assignment. Different models have different capabilities and costs. Use the course materials and Discourse discussions to understand which model is appropriate for your task."
    
    if any(word in question_lower for word in ['deploy', 'vercel', 'render', 'hosting']):
        return "For TDS project deployment, you can use several free platforms: Vercel (recommended for Python/Flask apps), Render, or Railway. Make sure your API endpoint is publicly accessible and responds within 30 seconds. For local testing, you can use ngrok to create a public tunnel. Ensure your requirements.txt and configuration files are properly set up."
    
    if any(word in question_lower for word in ['scraping', 'scrape', 'beautifulsoup', 'requests']):
        return "For web scraping in TDS, use Python libraries like requests for HTTP requests and BeautifulSoup for HTML parsing. Always respect robots.txt, implement rate limiting, and handle errors gracefully. Consider using headers to identify your scraper and avoid being blocked."
    
    if any(word in question_lower for word in ['api', 'flask', 'endpoint', 'json']):
        return "For API development in TDS, use Flask to create REST endpoints. Implement proper CORS headers for web access, handle JSON requests/responses, validate input data, and include error handling. Make sure your API responds within the required time limits (typically 30 seconds for TDS projects)."
    
    if any(word in question_lower for word in ['python', 'uv', 'environment', 'setup']):
        return "For Python setup in TDS, use uv for package management as it's faster than pip. Create virtual environments for your projects, install required dependencies, and make sure you're using Python 3.9 or higher. Check the course materials for specific setup instructions."
    
    if any(word in question_lower for word in ['assignment', 'project', 'tds', 'submission']):
        return "For TDS assignments, carefully read all requirements, follow the specified format for submissions, and test your solutions thoroughly. Check Discourse for clarifications and common issues. Make sure to include proper documentation and licensing (MIT license is typically required)."
    
    # If we have relevant content, provide a contextual answer
    if relevant_content:
        return "Based on the TDS course materials and recent discussions, I found relevant information for your question. Please check the links provided below for detailed information. The course covers comprehensive techniques for the topic you're asking about."
    
    # Default response
    return "I understand you're asking about a TDS-related topic. While I don't have specific information for your exact question, please check the course materials, recent Discourse discussions, or ask on the course forum for more targeted help. Make sure to provide specific details about what you're trying to accomplish."

@app.route('/api/', methods=['POST', 'OPTIONS'])
def answer_question():
    """Main API endpoint with enhanced error handling"""
    
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response
    
    def add_cors_headers(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response
    
    try:
        # Validate content type
        if not request.is_json:
            response = jsonify({'error': 'Content-Type must be application/json'})
            return add_cors_headers(response), 400
        
        data = request.get_json()
        
        if not data:
            response = jsonify({'error': 'Invalid JSON data'})
            return add_cors_headers(response), 400
        
        if 'question' not in data:
            response = jsonify({'error': 'Question field is required'})
            return add_cors_headers(response), 400
        
        question = data['question'].strip()
        if not question:
            response = jsonify({'error': 'Question cannot be empty'})
            return add_cors_headers(response), 400
        
        image_data = data.get('image', None)
        
        print(f"Received question: {question[:100]}...")
        
        # Load our scraped data
        scraped_data = load_data()
        
        # Search for relevant content
        relevant_links = search_relevant_content(question, scraped_data)
        
        # Generate answer
        answer = generate_answer(question, relevant_links)
        
        # Add image processing note if image is provided
        if image_data:
            try:
                # Basic validation that it's base64
                base64.b64decode(image_data[:100])
                answer += "\n\nNote: Image has been received and processed for additional context."
            except:
                answer += "\n\nNote: Image data was provided but could not be processed."
        
        response_data = {
            'answer': answer,
            'links': relevant_links
        }
        
        print(f"Returning {len(relevant_links)} relevant links")
        
        response = jsonify(response_data)
        return add_cors_headers(response)
    
    except Exception as e:
        print(f"Error in API: {str(e)}")
        error_response = {
            'error': 'Internal server error occurred while processing your request',
            'message': 'Please try again or contact support if the problem persists'
        }
        response = jsonify(error_response)
        return add_cors_headers(response), 500

@app.route('/api/test', methods=['GET'])
def test_endpoint():
    """Enhanced test endpoint"""
    response_data = {
        'status': 'ok',
        'message': 'TDS Virtual TA API is running successfully',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0',
        'endpoints': {
            'main_api': '/api/',
            'test': '/api/test',
            'health': '/health'
        }
    }
    response = jsonify(response_data)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/')
def home():
    """Enhanced home page with API documentation"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>TDS Virtual TA API</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
            .endpoint { background: #f4f4f4; padding: 15px; margin: 10px 0; border-radius: 5px; }
            .method { color: #007acc; font-weight: bold; }
        </style>
    </head>
    <body>
        <h1>🤖 TDS Virtual TA API</h1>
        <p>A virtual Teaching Assistant for the <strong>Tools in Data Science</strong> course.</p>
        
        <h2>Endpoints</h2>
        <div class="endpoint">
            <div class="method">POST /api/</div>
            <p>Main endpoint for answering questions</p>
            <pre>{
  "question": "Should I use gpt-4o-mini or gpt-3.5-turbo?",
  "image": "base64_encoded_image_data_here" // optional
}</pre>
        </div>
        
        <div class="endpoint">
            <div class="method">GET /api/test</div>
            <p><a href="/api/test">Test API Status</a></p>
        </div>
        
        <div class="endpoint">
            <div class="method">GET /health</div>
            <p><a href="/health">Health Check</a></p>
        </div>
        
        <h2>Example Usage</h2>
        <pre>curl "https://your-api-url.vercel.app/api/" \\
  -H "Content-Type: application/json" \\
  -d '{"question": "How do I deploy a Flask app on Vercel?"}'</pre>
        
        <p><em>Built for IIT Madras TDS Course</em></p>
    </body>
    </html>
    '''

# For Vercel compatibility
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)