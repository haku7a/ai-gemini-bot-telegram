import base64
import os
from google import genai
from google.genai import types


def generate(history):

    generated_answer = ''

    client = genai.Client(
        api_key=os.environ.get("YOUR_API_KEY"),
    )

    model = "gemini-2.0-flash"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(
                    text=str(history[:]),
                ),
            ],
        ),
    ]

    tools = [
        types.Tool(google_search=types.GoogleSearch())
    ]

    generate_content_config = types.GenerateContentConfig(
        tools=tools,
        response_mime_type="text/plain",
        system_instruction=[
            types.Part.from_text(text="""Отвечай максимально кратко, 
            НИКОГДА не выходя за пределы моего запроса, не раскрывай дополнительные вопросы."""),
        ],
    )

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        generated_answer += chunk.text

    return generated_answer
