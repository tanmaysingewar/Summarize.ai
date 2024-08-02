import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from groq import Groq

import requests

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import uuid
from dotenv import load_dotenv

from functions.filehandler import pdf_reader, docx_reader, txt_reader

from functions.file_download import download_file

from functions.index_generator import  add_document, query

load_dotenv()

# Initializes your app

app = App(token=os.getenv('SLACK_BOT_TOKEN'))

groq_client = Groq(
    api_key=os.getenv('GROQ_API_KEY'),
)

# Initializes your app with your bot token and socket mode handler
slack_client = WebClient(token=os.getenv('SLACK_BOT_TOKEN'))

# Listens to incoming messages that contain "hello"
@app.message("hello")
def message_hello(message, say):
    # say() sends a message to the channel where the event was triggered
    say(
        blocks=[
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"Hey there <@{message['user']}>!"},
                "accessory": {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Click Me"},
                    "action_id": "button_click"
                }
            }
        ],
        text=f"Hey there <@{message['user']}>!"
    )

@app.event("message")
def handle_message_events(body, logger):
    print("")

@app.event("file_shared")
def handle_file_share_events(body,say):
    print(body)
    file_id = body['event']["file_id"]
    try:
        # Retrieve file info
        result = slack_client.files_info(file=file_id)
        file_info = result["file"]
        download_url = file_info["url_private"]

        channel_id = body['event']["channel_id"]
        file_id = body['event']["file_id"]

        # Download the file using the URL
        headers = {"Authorization": f"Bearer {os.getenv('SLACK_BOT_TOKEN')}"}
        file_text = download_file(download_url, headers)
        if file_text is False:
            return say(f"File type not supported")

        add_document(channel_id, file_id, file_text)

        content = (
            f"Instruction: You are a summary generator, your job is to generate a summary of the given data. "
            f"You have to follow the instructions given on how to generate the summary. If no instruction is given, "
            f"then just generate the summary. Data: {file_text}"
            f"Instruction: The summary should be at least 200 words long."
        )

        chat_completion = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": content}],
            model="llama3-70b-8192",
        )

        say(f"{chat_completion.choices[0].message.content}")
    except SlackApiError as e:
        say(f"Error retrieving file info: {e.response['error']}")

@app.command("/chat")
def repeat_text(ack, respond, command,say):
    # Acknowledge command request
    print(command)
    ack()
    context = query(command["channel_id"], command["text"])
    print(context)

    content = (
        f"Role: You are the Q&A solver. Here is your information: Data: {context} "
        f"Using this information, answer the following question: Question: { command["text"]} "
        f"Instruction: Answer the question using the information provided in the data."
    )

    chat_completion = groq_client.chat.completions.create(
        messages=[{"role": "user", "content": content}],
        model="llama3-70b-8192",
    )

    # slack_client.chat_postEphemeral(channel=command["channel_id"], user=command["user_id"], text=chat_completion.choices[0].message.content)

    say(
        f"Hey there <@{command['user_name']}>! \n"
        f"You asked about : {command['text']} \n"
        f"By the give information, I can answer the question. \n"
        f"{chat_completion.choices[0].message.content}"
    )

@app.action("button_click")
def action_button_click(body, ack, say):
    # Acknowledge the action
    ack()
    say(f"<@{body['user']['id']}> clicked the button")

SocketModeHandler(app, os.getenv('SLACK_BOT_SOCKET_TOKEN')).start()
 