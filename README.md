### 4. README.md
```markdown
# TDS Virtual TA

A virtual Teaching Assistant for the Tools in Data Science course that automatically answers student questions based on course content and Discourse discussions.

## Features

- Scrapes TDS course content and Discourse posts
- Provides an API endpoint for answering questions
- Supports text and image inputs
- Returns relevant links and sources

## Setup

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the scraper: `python scraper.py`
4. Start the API: `python app.py`

## API Usage

POST to `/api/` with JSON:

```json
{
  "question": "Should I use gpt-4o-mini or gpt-3.5-turbo?",
  "image": "base64_encoded_image_data_here"
}
```

Response:
```json
{
  "answer": "Use the specific model mentioned in the question...",
  "links": [
    {
      "url": "https://discourse.example.com/post/123",
      "text": "Relevant discussion about model selection"
    }
  ]
}
```

## Deployment

This app can be deployed on:
- Vercel (recommended for free tier)
- Render
- Railway
- Or use ngrok for local testing

## License

MIT License
```