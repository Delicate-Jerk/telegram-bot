import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Token for the testing bot
TEST_BOT_TOKEN = ""
# Group Chat ID obtained from the previous script
GROUP_CHAT_ID = ""
# API URL for Telegram Bot API
API_URL = f"https://api.telegram.org/bot{TEST_BOT_TOKEN}"

def send_start_command():
    # Construct the URL to send a message
    url = f"{API_URL}/sendMessage"

    # Payload to send the /start command
    payload = {
        "chat_id": GROUP_CHAT_ID,
        "text": "/start"
    }

    # Send the request
    response = requests.post(url, json=payload)

    if response.status_code == 200:
        print("Successfully sent the /start command to the group.")
    else:
        print(f"Failed to send the /start command: {response.text}")

if __name__ == "__main__":
    send_start_command()
