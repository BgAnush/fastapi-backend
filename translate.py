from deep_translator import GoogleTranslator

def translate_text(text: str, target_lang: str) -> str:
    """Translate single string text."""
    return GoogleTranslator(source="auto", target=target_lang).translate(text)

def translate_page(data: dict, target_lang: str) -> dict:
    """Translate all string values in a dictionary."""
    translated_data = {}
    for key, value in data.items():
        if isinstance(value, str):
            translated_data[key] = translate_text(value, target_lang)
        elif isinstance(value, dict):
            translated_data[key] = translate_page(value, target_lang)
        elif isinstance(value, list):
            translated_data[key] = [
                translate_text(item, target_lang) if isinstance(item, str) else item
                for item in value
            ]
        else:
            translated_data[key] = value
    return translated_data

def translate_page_multiple_languages(data: dict, languages: list) -> dict:
    """Translate page into multiple languages at once."""
    result = {}
    for lang in languages:
        result[lang] = translate_page(data, lang)
    return result
