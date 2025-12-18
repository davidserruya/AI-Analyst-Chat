def call_gemini(model, prompt: str) -> str:
    response = model.generate_content(prompt)
    return response.text.strip()
