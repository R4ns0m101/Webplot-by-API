from mistralai import Mistral
import os, dotenv

dotenv.load_dotenv(dotenv.find_dotenv())

client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

SYSTEM_PROMPT = """
You convert user requests into a SINGLE valid Python math expression in terms of x.

Rules:
- Use only x and math (math.sin, math.cos, math.exp, math.log, math.pi)
- Output ONLY the expression
- No explanations
- No backticks

Examples:
"plot sine wave" -> math.sin(x)
"x squared plus 2" -> x**2 + 2
"""

def text_to_expression(user_text: str) -> str:
    resp = client.chat.complete(
        model="mistral-small-latest",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text}
        ],
        temperature=0
    )
    return resp.choices[0].message.content.strip()
