import json
from openai import AsyncOpenAI
from google.cloud import vision
from google.oauth2 import service_account
from app.config import settings

openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

# Setup Google Vision from JSON string env var
google_creds = service_account.Credentials.from_service_account_info(
    json.loads(settings.GOOGLE_APPLICATION_CREDENTIALS_JSON)
)
google_client = vision.ImageAnnotatorClient(credentials=google_creds)

async def identify_books(image_url: str):
    """primary pipline: GPT-4o -> fallback: Google Vision"""
    print(f"Scanning image: {image_url}")

    try:
        response = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Return JSON only. Identify book in the image. Format: {'book': [{'title': 'str', 'author': 'str'}]}"},
                {"role": "user", "content":[
                    {"type": "text", "text": "Identify these books."},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]}
            ],
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        return json.loads(content).get('books', [])
    except Exception as e:
        print(f"GPT-4o failed ({e}). Attempting Google Fallback...")
        return await _fallback_scan(image_url)
    
async def _fallback_scan(image_url: str):
    """Google Vision OCR + GPT-3.5 cleanup"""
    image = vision.Image()
    image.source.image_uri = image_url

    # Synchronous Google call (blocking), ideally run in threadpool
    response = google_client.text_detection(image=image)
    texts = response.text_annotations

    if not texts:
        return []
    
    raw_text = texts[0].description

    # Cheap GPT-3.5 cleanup
    cleanup = await openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Extact book title/authors from this OCR text. Return JSON: {'books': [...]}"},
            {"role": "user", "content": raw_text}
        ],
        response_format={"type": "json_object"}
    )
    return json.loads(cleanup.choices[0].message.content).get('books', [])