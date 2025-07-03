import os
from flask import Flask, request
import requests
from openai import OpenAI

# Load secrets from environment variables
GROUPME_BOT_ID = os.environ["GROUPME_BOT_ID"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

GROUPME_POST_URL = "https://api.groupme.com/v3/bots/post"

# Initialize OpenAI client
openai_client = OpenAI(api_key=OPENAI_API_KEY)

app = Flask(__name__)

def send_groupme_message(text):
    payload = {
        "bot_id": GROUPME_BOT_ID,
        "text": text
    }
    requests.post(GROUPME_POST_URL, json=payload)

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()

    # Ignore messages from the bot itself
    if data.get("sender_type") == "bot":
        return "ok", 200

    sender_name = data.get("name")
    message_text = data.get("text", "")

    # Only respond if bot is mentioned
    if "@Jeff" in message_text:
        prompt = f"""
        Someone named {sender_name} said: "{message_text}"

        Craft an extremely rude, comedic trash-talk reply.
        - Keep it comedic and edgy.
        - Avoid slurs or hateful language.
        - Keep it under 2-3 sentences.
        """

        ai_response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a savage AI bot whose sole purpose is to roast "
                        "and insult anyone who talks to you in GroupMe. "
                        "Avoid hateful or violent content."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.9,
        )

        roast = ai_response.choices[0].message.content.strip()

        send_groupme_message(roast)

    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
