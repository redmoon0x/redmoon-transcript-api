from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import json
import time
import random
from typing import Optional, Dict, Any
from fake_useragent import UserAgent
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

app = Flask(__name__)
CORS(app)

class RateLimiter:
    def __init__(self, max_per_minute=10):
        self.max_per_minute = max_per_minute
        self.requests = []
    
    def wait_if_needed(self):
        now = time.time()
        # Remove requests older than 1 minute
        self.requests = [req_time for req_time in self.requests if now - req_time < 60]
        
        if len(self.requests) >= self.max_per_minute:
            # Wait until we can make another request
            sleep_time = 60 - (now - self.requests[0])
            if sleep_time > 0:
                time.sleep(sleep_time)
        
        self.requests.append(now)

def create_session() -> requests.Session:
    session = requests.Session()
    
    # Configure retries
    retries = Retry(
        total=3,  # total number of retries
        backoff_factor=0.5,  # wait 0.5, 1, 2... seconds between retries
        status_forcelist=[429, 500, 502, 503, 504]  # status codes to retry on
    )
    
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))
    
    return session

def get_transcript(youtube_url: str) -> Optional[str]:
    # Initialize rate limiter (10 requests per minute max)
    rate_limiter = RateLimiter(max_per_minute=10)
    
    # URL of the target website
    base_url = "https://api.kome.ai/api/tools/youtube-transcripts"
    
    # Generate random User-Agent
    ua = UserAgent()
    
    # Make the POST request to submit the URL
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': ua.random,
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.5',
        'DNT': '1'
    }
    
    # Prepare JSON data
    data = {
        "video_id": youtube_url,
        "format": True
    }
    
    session = create_session()
    
    try:
        # Apply rate limiting
        rate_limiter.wait_if_needed()
        
        # Add random delay between requests (0.5 to 2 seconds)
        time.sleep(random.uniform(0.5, 2))
        
        # Make POST request to API endpoint
        response = session.post(base_url, json=data, headers=headers)
        
        # Check if request was successful
        if response.status_code == 200:
            try:
                result = response.json()
                if result and 'transcript' in result:
                    return result['transcript']
            except json.JSONDecodeError:
                print("Failed to parse JSON response")
                
        print(f"Debug - Status Code: {response.status_code}")
        print(f"Debug - Response Content: {response.text[:500]}")
        
        if response.status_code == 429:
            print("Rate limit exceeded. Waiting before retrying...")
            time.sleep(30)  # Wait 30 seconds before retrying
            return get_transcript(youtube_url)  # Retry the request
            
        return "Transcript not found. Please make sure the URL is valid and the video has captions available."
    except requests.RequestException as e:
        print(f"Network error occurred: {str(e)}")
        return f"Error fetching transcript: {str(e)}"
    finally:
        session.close()

@app.route('/get-transcript', methods=['POST'])
def get_transcript_route() -> Dict[str, Any]:
    data = request.get_json()
    
    if not data or 'url' not in data:
        return jsonify({
            'error': 'Missing YouTube URL',
            'status': 'error'
        }), 400
    
    try:
        youtube_url = data['url']
        transcript = get_transcript(youtube_url)
        
        if transcript.startswith("Error"):
            return jsonify({
                'error': transcript,
                'status': 'error'
            }), 500
        
        return jsonify({
            'transcript': transcript,
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/health', methods=['GET'])
def health_check() -> Dict[str, str]:
    return jsonify({
        'status': 'healthy',
        'message': 'YouTube Transcript Generator API is running'
    })

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
