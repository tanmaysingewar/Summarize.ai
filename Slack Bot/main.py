import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

import groq
from groq import Groq

import requests

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import uuid
from dotenv import load_dotenv

from functions.filehandler import pdf_reader, docx_reader, txt_reader
from functions.file_download import download_file
from functions.index_generator import add_document, query

load_dotenv()

print(os.getenv('SLACK_BOT_TOKEN'))
print(os.getenv('GROQ_API_KEY'))
print(os.getenv('SLACK_BOT_SOCKET_TOKEN'))

# Initializes your app
app = App(token=os.getenv('SLACK_BOT_TOKEN'))

groq_client = Groq(
    api_key=os.getenv('GROQ_API_KEY'),
)

# Initializes your app web client
slack_client = WebClient(token=os.getenv('SLACK_BOT_TOKEN'))

@app.event("message")
def handle_message_events(body, logger):
    try : 
        print("")
    except SlackApiError as e:
        print(e)
    except:
        print("An unknown error occurred")

@app.event("file_shared")
def handle_file_share_events(body,say):
    try:
        file_id = body['event']["file_id"]
        # Retrieve file info
        result = slack_client.files_info(file=file_id)
        file_info = result["file"]
        download_url = file_info["url_private"]

        say(f"Hey there <@{body['event']['user_id']}>! I got the file you shared, I am summarizing it now.")

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
        # say(f"Error retrieving file info: {e.response['error']}")
        say(f"Sorry <@{body['event']['user_id']}> 😕, I am unable to summarize your file. Please try again later.")
    except groq.APIConnectionError as e:
        say(f"Sorry <@{body['event']['user_id']}> 😕, I am unable to summarize your file. Please try again later.")
    except groq.RateLimitError as e:
        say(f"Sorry <@{body['event']['user_id']}> 😕, As the file is too long, I am unable to summarize it. We will soon come up with a version that can handle large files.")
    except groq.APIStatusError as e:
        say(f"Sorry <@{body['event']['user_id']}> 😕, I am unable to summarize your file. Please try again later.")
    except groq.APIError as e:
        say(f"Sorry <@{body['event']['user_id']}> 😕, I am unable to summarize your file. Please try again later.")
    except :
        say(f"Sorry <@{body['event']['user_id']}> 😕, I am unable to summarize your file. Please try again later.")


@app.command("/chat")
def repeat_text(ack, respond, command,say):
    try:
        ack()
        context = query(command["channel_id"], command["text"])

        content = (
            f"Role: You are the Q&A solver. Here is your information: Data: {context} "
            f"Using this information, answer the following question: Question: { command["text"]} "
            f"Instruction: Answer the question using the information provided in the data."
            f"Note : 1) Try to user emoji's in response"
            f"2) try to break the response in multiple lines"
            f"3) dont repeat the question in response"
        )

        chat_completion = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": content}],
            model="llama3-70b-8192",
        )

        say(
            f"Hey there <@{command['user_name']}>! \n"
            f"You asked about : `{command['text']}` \n"
            f"{chat_completion.choices[0].message.content}"
        )
    except SlackApiError as e:
        say(f"Sorry <@{command['user_name']}> 😕, I am unable to answer your question. Please try again later.")
    except groq.APIConnectionError as e:
        say(f"Sorry <@{command['user_name']}> 😕, I am unable to answer your question. Please try again later.")
    except groq.RateLimitError as e:
        say(f"Sorry <@{command['user_name']}> 😕, I am unable to answer your question. Please try again later.")
    except groq.APIStatusError as e:
        say(f"Sorry <@{command['user_name']}> 😕, I am unable to answer your question. Please try again later.")
    except groq.APIError as e:
        say(f"Sorry <@{command['user_name']}> 😕, I am unable to answer your question. Please try again later.")
    except :
        say(f"Sorry <@{command['user_name']}> 😕, I am unable to answer your question. Please try again later.")

@app.command("/privatechat")
def repeat_text(ack, respond, command,say):
    error_response = (
        f"Sorry <@{command['user_name']}> 😕, I am unable to answer your question. Please try again later."
    )
    try:
        ack()
        context = query(command["channel_id"], command["text"])

        content = (
            f"Role: You are the Q&A solver. Here is your information: Data: {context} "
            f"Using this information, answer the following question: Question: { command["text"]} "
            f"Instruction: Answer the question using the information provided in the data."
        )

        chat_completion = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": content}],
            model="llama3-70b-8192",
        )

        response = (
            f"Hi <@{command['user_name']}>! \n"
            f"You asked about : `{command['text']}` \n"
            f"{chat_completion.choices[0].message.content}"
        )

        slack_client.chat_postEphemeral(channel=command["channel_id"], user=command["user_id"], text=response)
    
    except SlackApiError as e:
        slack_client.chat_postEphemeral(channel=command["channel_id"], user=command["user_id"], text=error_response)
    except groq.APIConnectionError as e:
        slack_client.chat_postEphemeral(channel=command["channel_id"], user=command["user_id"], text=error_response)
    except groq.RateLimitError as e:
        slack_client.chat_postEphemeral(channel=command["channel_id"], user=command["user_id"], text=error_response)
    except groq.APIStatusError as e:
        slack_client.chat_postEphemeral(channel=command["channel_id"], user=command["user_id"], text=error_response)
    except groq.APIError as e:
        slack_client.chat_postEphemeral(channel=command["channel_id"], user=command["user_id"], text=error_response)
    except :
        slack_client.chat_postEphemeral(channel=command["channel_id"], user=command["user_id"], text=error_response)

@app.command("/help")
def helpCommand(ack,respond,command,say):
    try:
        ack()

        message = (
            f"Hi <@{command['user_name']}>! 🎉. Seems like need Help \n"
            f"I am an Intelligent Summarizer Bot powered by <https://ai-gurukul.vercel.app|*AIGurukul*> , here to make your life easier! I can handle PDF, TXT, and DOCS files, and I'll promptly summarize them if they're not too long. 📄✨\n"
            f"Ready to get started? \n"
            f"Just upload a file and I'll summarize it for you! 📄\n"
            f"Here are some commands you can try: \n"
            f" - `/chat`: Chat with the uploaded documents and get the information you need in a snap! 💬\n"
            f" - `/help`: Discover more about my capabilities and how I can assist you every step of the way! 🤖\n"
            f" - `/privatechat`: Private Chat response will be visible to the you only 🤫\n"
            f"Let's make document handling a breeze! 🚀"
        )

        slack_client.chat_postEphemeral(channel=command["channel_id"], user=command["user_id"], text=message)
    except SlackApiError as e:
        say(f"Sorry 😕, I am unable help you. Please try again later.")

@app.event("app_mention")
def handle_app_mention_events(body,say):
    try : 
        userQuery = body['event']['text']
        user_id = body['event']['user']

        context = (
            f"Here is the Context who you are : "
            f"You are the Intelligent Bot powered by AIGurukul, You can take PDF, TXT and DOCS files, which you will promptly summarize if the file is not very long. \n"
            f"Here are some commands you can perform \n"
            f" - `/chat` : You can Chat with the Uploaded Documents \n"
            f" - `/help` : I will tell you about my self and how I can help you\n"
            f" - `/privatechat`: Private Chat response will be visible to the you only 🤫\n"
            f"And here is her is the query ask by the user : {userQuery}"
            f"Note : Respond in few words only like 20 to 30 words, no long messages"
            f"First greed the user while responding"
            f"Hey there <@{user_id}> or any other way"
            f"If question is asked starts with the accordingly "
            f"But only user this id only {user_id} for mentioning the user"
        )

        response_to_query = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": context}],
            model="llama3-70b-8192",
        )

        say(
            f"{response_to_query.choices[0].message.content}"
        )
    except SlackApiError as e:
        say(f"Sorry <@{body['event']['user_id']}> 😕, I am unable to respond to your message. Please try again later.")
    except groq.APIConnectionError as e:
        say(f"Sorry <@{body['event']['user_id']}> 😕, I am unable to respond to your message. Please try again later.")
    except groq.RateLimitError as e:
        say(f"Sorry <@{body['event']['user_id']}> 😕, I am unable to respond to your message. Please try again later.")
    except groq.APIStatusError as e:
        say(f"Sorry <@{body['event']['user_id']}> 😕, I am unable to respond to your message. Please try again later.")
    except groq.APIError as e:
        say(f"Sorry <@{body['event']['user_id']}> 😕, I am unable to respond to your message. Please try again later.")
    except :
        say(f"Sorry <@{body['event']['user_id']}> 😕, I am unable to respond to your message. Please try again later.")


@app.event('member_joined_channel')
def member_joined_channel(body,say):
    try : 
        message = (
            f"Hi <@{body['event']['user']}>! 🎉 Welcome to the channel! 🚀\n"
            f"I am an Intelligent Summarizer Bot powered by <https://ai-gurukul.vercel.app|*AIGurukul*> , here to make your life easier! I can handle PDF, TXT, and DOCS files, and I'll promptly summarize them if they're not too long. 📄✨\n"
            f"Ready to get started? Here are some commands you can try: \n"
            f"Just upload a file and I'll summarize it for you! 📄\n"
            f" - `/chat`: Chat with the uploaded documents and get the information you need in a snap! 💬\n"
            f" - `/help`: Discover more about my capabilities and how I can assist you every step of the way! 🤖\n"
            f" - `/privatechat`: Private Chat response will be visible to the you only 🤫\n"
            f"Let's make document handling a breeze! 🚀"
        )

        response = {
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": message
                        }
                    }
                ]
            }
        say(message)
    except :
        print("An unknown error occurred")

SocketModeHandler(app, os.getenv('SLACK_BOT_SOCKET_TOKEN')).start()