"""Get structured (JSON) output from an LLM through the DataRobot LLM gateway.

Technique: prefill the assistant turn with an opening code fence and stop
generation at the closing fence, so the reply contains only the JSON.
"""
import json
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

DR_ENDPOINT = os.environ.get("DATAROBOT_ENDPOINT", "https://app.datarobot.com/api/v2")
MODEL = os.environ.get("STRUCTURED_DATA_MODEL", "azure/gpt-4o-mini")


def get_client():
    return OpenAI(
        base_url=f"{DR_ENDPOINT}/genai/llmgw",
        api_key=os.environ["DATAROBOT_API_TOKEN"],
    )


def add_user_message(messages, text):
    messages.append({"role": "user", "content": text})


def add_assistant_message(messages, text):
    messages.append({"role": "assistant", "content": text})


def chat(client, messages, model=MODEL, stop_sequences=None, max_output_tokens=1000):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        stop=stop_sequences,
        max_tokens=max_output_tokens,
    )
    return response.choices[0].message.content


def parse_json_reply(text):
    """Strip any leftover code fence and parse the JSON."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else ""
    text = text.removesuffix("```").strip()
    return json.loads(text)


def main():
    client = get_client()
    messages = []
    add_user_message(
        messages,
        "Generate three different sample AWS CLI commands. Each command should be very short. "
        'Return only a JSON array of strings, for example ["aws s3 ls"]. '
        "No explanations, no extra text.",
    )
    add_assistant_message(messages, "```json")

    text = chat(client, messages, stop_sequences=["```"])
    commands = parse_json_reply(text)
    print("; ".join(commands))
    return commands


if __name__ == "__main__":
    main()
