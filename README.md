# YouTube Transcript Generator

This project provides a Flask-based API to fetch transcripts for YouTube videos. It uses the `kome.ai` API to retrieve the transcripts and includes rate limiting to avoid hitting API limits.

## Features

- Fetches transcripts for YouTube videos.
- Rate limiting to avoid exceeding API request limits.
- Randomized User-Agent to mimic different browsers.
- Health check endpoint to verify the API is running.

## Requirements

- Python 3.6+
- Flask
- Flask-CORS
- requests
- BeautifulSoup4
- fake_useragent

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/yt-transcript-generator.git
    cd yt-transcript-generator
    ```

2. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. Run the Flask application:
    ```bash
    python transcript_generator.py
    ```

2. The API will be available at `http://0.0.0.0:5000`.

## Endpoints

### Get Transcript

- **URL:** `/get-transcript`
- **Method:** `POST`
- **Request Body:**
    ```json
    {
        "url": "YouTube video URL"
    }
    ```
- **Response:**
    ```json
    {
        "transcript": "Transcript text",
        "status": "success"
    }
    ```

### Health Check

- **URL:** `/health`
- **Method:** `GET`
- **Response:**
    ```json
    {
        "status": "healthy",
        "message": "YouTube Transcript Generator API is running"
    }
    ```

## Example

To get the transcript of a YouTube video, send a POST request to `/get-transcript` with the YouTube video URL in the request body.

```bash
curl -X POST http://0.0.0.0:5000/get-transcript -H "Content-Type: application/json" -d '{"url": "https://www.youtube.com/watch?v=example"}'
```

## License

This project is licensed under the MIT License.
