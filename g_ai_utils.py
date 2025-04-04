import base64
import os
from google import genai
from google.genai import types
from config import RESPONSE_INSTRUCTION


def generate(history):

    generated_answer = ''
    contents = []

    client = genai.Client(
        api_key=os.environ.get("YOUR_API_KEY"),
    )

    model = "gemini-2.0-flash"

    for history_item in history:
        contents.append(types.Content(
            role=history_item['role'],
            parts=[
                types.Part.from_text(
                    text=history_item['parts']),
            ],
        ),
        )

    tools = [
        types.Tool(google_search=types.GoogleSearch())
    ]

    generate_content_config = types.GenerateContentConfig(
        temperature=1,
        top_p=1,
        tools=tools,
        response_mime_type="text/plain",
        system_instruction=[
            types.Part.from_text(text=RESPONSE_INSTRUCTION),
        ],
    )

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        generated_answer += chunk.text

    return generated_answer
