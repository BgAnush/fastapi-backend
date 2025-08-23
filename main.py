from fastapi import FastAPI
from pydantic import BaseModel
from translate import translate_page_multiple_languages

app = FastAPI()

class PageRequest(BaseModel):
    data: dict
    languages: list  # Example: ["en", "kn", "hi", "te", "ta"]

@app.post("/translate_page_multi")
def translate_page_multi(req: PageRequest):
    """
    Translate full JSON page into multiple languages
    Request:
    {
      "data": { "title": "Hello", "body": "How are you?" },
      "languages": ["en", "kn", "hi", "te", "ta"]
    }
    """
    translated_data = translate_page_multiple_languages(req.data, req.languages)
    return {"original": req.data, "translated": translated_data}
