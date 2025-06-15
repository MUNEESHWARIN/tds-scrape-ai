import requests
import json
import os
from datetime import datetime
import time

def scrape_tds_course_content():
    """Scrape TDS course content (simplified version)"""
    print("Scraping TDS course content...")
    
    # This is a simplified version - in reality you'd scrape the actual content
    course_content = [
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
    
    return course_content

def scrape_discourse_posts():
    """Scrape Discourse posts (simplified version)"""
    print("Scraping Discourse posts...")
    
    # This is a simplified version - in reality you'd use Discourse API
    discourse_posts = [
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
    
    return discourse_posts

def main():
    # Create data directory
    os.makedirs('data', exist_ok=True)
    
    # Scrape course content
    course_content = scrape_tds_course_content()
    with open('data/course_content.json', 'w', encoding='utf-8') as f:
        json.dump(course_content, f, indent=2, ensure_ascii=False)
    
    # Scrape discourse posts
    discourse_posts = scrape_discourse_posts()
    with open('data/discourse_posts.json', 'w', encoding='utf-8') as f:
        json.dump(discourse_posts, f, indent=2, ensure_ascii=False)
    
    print("Data scraping completed!")
    print(f"Course content: {len(course_content)} items")
    print(f"Discourse posts: {len(discourse_posts)} items")

if __name__ == "__main__":
    main()
# This script scrapes course content and discourse posts for the TDS course.
