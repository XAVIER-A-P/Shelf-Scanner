import json
from openai import AsyncOpenAI
from app.config import settings

openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

async def generate_recommendations(detected_books: list) -> list:
    """
    Takes a list of raw books {'title': '...', 'author': '...'}
    Returns the same list augmented with 'score' and 'reason'.
    """
    if not detected_books:
        return []

    print(f"Generating recommendations for {len(detected_books)} books...")

    prompt = f"""
    You are an expert librarian. I am looking at a bookshelf with these books:
    {json.dumps(detected_books)}
    
    For each book, provide:
    1. A 'reason': A short, compelling 1-sentence hook on why I should read it.
    2. A 'score': A recommendation score from 0 to 100 based on general critical acclaim and popularity.
    
    Return ONLY a JSON object with a single key 'books' containing an array of objects. 
    Each object MUST have these exact keys: 'title', 'author', 'reason', 'score'.
    """

    try:
        response = await openai_client.chat.completions.create(
            model="gpt-3.5-turbo", # Fast and cheap for text analysis
            messages=[
                {"role": "system", "content": "You are a data-formatting robot. Output strictly valid JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        recommended_data = json.loads(content).get('books', [])
        
        # Sort books by highest score first
        recommended_data.sort(key=lambda x: x.get('score', 0), reverse=True)
        return recommended_data

    except Exception as e:
        print(f"Recommendation generation failed: {e}")
        # Fallback: Just return the original books if the LLM fails
        return detected_books