#!/usr/bin/env python3
"""
Test script for TDS Virtual TA API
"""
import requests
import json
import sys

def test_api(base_url):
    """Test the API endpoint"""
    api_url = f"{base_url}/api/"
    
    # Test cases
    test_cases = [
        {
            "name": "GPT Model Question",
            "payload": {
                "question": "Should I use gpt-4o-mini or gpt-3.5-turbo for GA5?"
            }
        },
        {
            "name": "Deadline Question",
            "payload": {
                "question": "What is the deadline for GA5?"
            }
        },
        {
            "name": "API Usage Question",
            "payload": {
                "question": "How should I use APIs in my assignments?"
            }
        },
        {
            "name": "Python Setup Question",
            "payload": {
                "question": "How do I set up Python environment for TDS?"
            }
        }
    ]
    
    print(f"Testing API at: {api_url}")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['name']}")
        print(f"Question: {test_case['payload']['question']}")
        
        try:
            response = requests.post(
                api_url, 
                json=test_case['payload'],
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Answer: {data.get('answer', 'No answer')}")
                print(f"Links: {len(data.get('links', []))} links provided")
                
                # Check if response format is correct
                if 'answer' in data and 'links' in data:
                    print("✅ Response format is correct")
                else:
                    print("❌ Response format is incorrect")
            else:
                print(f"❌ Error: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
        
        print("-" * 30)

def test_health_endpoint(base_url):
    """Test health endpoint"""
    health_url = f"{base_url}/health"
    
    try:
        response = requests.get(health_url, timeout=10)
        print(f"Health check: {response.status_code} - {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

if __name__ == "__main__":
    # Default to localhost, but allow command line argument
    if len(sys.argv) > 1:
        base_url = sys.argv[1].rstrip('/')
    else:
        base_url = "http://localhost:5000"
    
    print("TDS Virtual TA API Test Script")
    print("=" * 50)
    
    # Test health endpoint first
    print("Testing health endpoint...")
    if test_health_endpoint(base_url):
        print("✅ Health endpoint is working")
    else:
        print("❌ Health endpoint is not working")
    
    # Test main API
    test_api(base_url)
    
    print("\nTest completed!")
    print("\nTo test with your deployed URL, run:")
    print("python test_api.py https://your-app.vercel.app")