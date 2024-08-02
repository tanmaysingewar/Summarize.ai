from fastapi import FastAPI,File,UploadFile,Form
from pydantic import BaseModel
from typing_extensions import Annotated
from typing import Union

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

import os
from groq import Groq
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from langchain_text_splitters import RecursiveCharacterTextSplitter

import random
import re

from docx import Document
from PyPDF2 import PdfReader
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import traceback

import requests
import json

url = "https://api.transcribetube.com/api/transcribeVideo"


UPLOAD_DIR = Path() / "upload"

client = Groq(
    api_key="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",
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins= ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class YTTranscript(BaseModel):
    yt_link: str
    title: str


def chunk_text(text, chunk_size=500):
    words = text.split()
    return [' '.join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]

def extract_video_id(url):
    pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None

def parse_quiz(response):
        question_blocks = re.split(r"\*\*Question \d+:\*\*", response)[1:]
        parsed_quiz = []

        for block in question_blocks:
            question_match = re.search(r"^(.*?)\n", block)
            question_text = question_match.group(1).strip() if question_match else block.strip()
            
            options = re.findall(r"\*\*Option (\d+):\*\* (.*?)\n", block)
            formatted_options = [f"{opt[1]}" for opt in options]

            answer_match = re.search(r"\*\*Answer:\*\* (\d+)", block)
            answer_option = answer_match.group(1) if answer_match else ""

            parsed_quiz.append({
                "question": question_text,
                "options": formatted_options,
                "answer": answer_option
            })

        return parsed_quiz


class DocumentStore:
    def __init__(self):
        self.documents = []
        self.vectorizer = TfidfVectorizer()
        self.document_matrix = None

    def add_document(self, text):
        new_chunks = chunk_text(text)
        self.documents.extend(new_chunks)
        self.document_matrix = self.vectorizer.fit_transform(self.documents)

    def query(self, userPrompt, top_k=5):
        if not self.documents:
            return []
        query_vector = self.vectorizer.transform([userPrompt])
        similarities = cosine_similarity(query_vector, self.document_matrix).flatten()
        indices = similarities.argsort()[-top_k:][::-1]
        return [self.documents[i] for i in indices]

@app.get("/")
def read_root():
    print("Health Check")
    return {"status": "ok"}


def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    number_of_pages = len(reader.pages)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    os.remove(file_path)
    return text

def extract_text_from_docx(file_path):
    doc = Document(file_path)
    para = doc.paragraphs
    text = ""
    for p in para:
        text += p.text
    os.remove(file_path)
    return text

def extract_text_from_txt(file_path):
    with open(file_path, "r") as f:
        text = f.read()
    os.remove(file_path)
    return text

@app.post("/summarize")
async def file_summary(
    upload_file: Annotated[UploadFile, File()],
    userPrompt: Annotated[str, Form()] = None):
    try:
        file_read = await upload_file.read()
        file_path = os.path.join(UPLOAD_DIR, upload_file.filename)
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(file_read)

        if upload_file.filename.endswith(".pdf"):
            text = extract_text_from_pdf(file_path)
        elif upload_file.filename.endswith(".docx"):
            text = extract_text_from_docx(file_path)
        elif upload_file.filename.endswith(".txt"):
            text = extract_text_from_txt(file_path)
        else:
            return {"error": "Unsupported file type"}
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,
            length_function=len,
            is_separator_regex=False,
        )

        chunk = text_splitter.create_documents([text])

        combined_text = ""
        for i in range(4):
            combined_text += str(random.choice(chunk))

        
        content = (
            f"Instruction: You are a summary generator, your job is to generate a summary of the given data. "
            f"You have to follow the instructions given on how to generate the summary. If no instruction is given, "
            f"then just generate the summary. Data: {combined_text} Instruction: {userPrompt} "
            f"Instruction: The summary should be at least 200 words long."
        )

        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": content}],
            model="llama3-70b-8192",
        )

        return chat_completion.choices[0].message.content
    except Exception as e:
        return {"error": str(e)}

@app.post("/chat")
async def file_chat(
    upload_file: UploadFile = File(...),
    userPrompt: str = Form(None)):
    try:
        # Read and save the uploaded file
        file_read = await upload_file.read()
        file_path = os.path.join(UPLOAD_DIR, upload_file.filename)
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(file_read)

        # Extract text based on file type
        if upload_file.filename.endswith(".pdf"):
            text = extract_text_from_pdf(file_path)
        elif upload_file.filename.endswith(".docx"):
            text = extract_text_from_docx(file_path)
        elif upload_file.filename.endswith(".txt"):
            text = extract_text_from_txt(file_path)
        else:
            return JSONResponse({"error": "Unsupported file type"})

        store = DocumentStore()
        
        store.add_document(text)

        if not userPrompt:
            userPrompt = ""

        relevant_chunks = store.query(userPrompt, top_k=5)
        combined_text = " ".join(relevant_chunks)

        content = (
            f"Role: You are the Q&A solver. Here is your information: Data: {combined_text} "
            f"Using this information, answer the following question: Question: {userPrompt} "
            f"Instruction: Answer the question using the information provided in the data."
        )

        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": content}],
            model="llama3-70b-8192",
        )

        # Return the chat completion result
        return chat_completion.choices[0].message.content
    
    except Exception as e:
        print(e)
        return JSONResponse({"error": str(e)})

@app.post("/quiz")
async def quiz(
    upload_file: Annotated[UploadFile, File()]):
    try:
        file_read = await upload_file.read()
        file_path = os.path.join(UPLOAD_DIR, upload_file.filename)
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(file_read)

        if upload_file.filename.endswith(".pdf"):
            text = extract_text_from_pdf(file_path)
        elif upload_file.filename.endswith(".docx"):
            text = extract_text_from_docx(file_path)
        elif upload_file.filename.endswith(".txt"):
            text = extract_text_from_txt(file_path)
        else:
            return {"error": "Unsupported file type"}

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,
            length_function=len,
            is_separator_regex=False,
        )

        chunk = text_splitter.create_documents([text])

        combined_text = ""
        for i in range(4):
            combined_text += str(random.choice(chunk))


        content = (
            f"Generate a quiz based on the following information: Data: {combined_text} "
            f"Instructions :"
            f"1. Generate a quiz based on the given information."
            f"2. The quiz should be at least 10 questions long."
            f"3. The quiz should be in the form of a list of questions and options."
            f"Format of the quiz:"
            f"Each question should be start with **Question :***"
            f"Option should be start with **Option :***"
            f"Each answer should be like **Answer :*** and only give the option number for the answer"
            f"Options: 1, 2, 3, 4"
            f"Answer: Answer"
        ) 

        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": content}],
            model="llama3-70b-8192",
        )

        
        def parse_quiz(response):
            question_blocks = re.split(r"\*\*Question \d+:\*\*", response)[1:]
            parsed_quiz = []

            for block in question_blocks:
                question_match = re.search(r"^(.*?)\n", block)
                question_text = question_match.group(1).strip() if question_match else block.strip()
                
                options = re.findall(r"\*\*Option (\d+):\*\* (.*?)\n", block)
                formatted_options = [f"{opt[1]}" for opt in options]

                answer_match = re.search(r"\*\*Answer:\*\* (\d+)", block)
                answer_option = answer_match.group(1) if answer_match else ""

                parsed_quiz.append({
                    "question": question_text,
                    "options": formatted_options,
                    "answer": answer_option
                })

            return parsed_quiz

        
        print(chat_completion.choices[0].message.content)
        json_format =  parse_quiz(chat_completion.choices[0].message.content) 
        print(json_format)

        json_format = json.dumps(json_format)
        print(json_format)

        json_compatible_item_data = jsonable_encoder(json_format)
        print(json_compatible_item_data)

        return JSONResponse(content=json_compatible_item_data)

    except Exception as e:
        print(e)
        return {"error": str(e)}

@app.post("/ytsummarize")
def yt_summary(
    yt_link: Annotated[str, Form()] = None,
    userPrompt: Annotated[str, Form()] = None):
    try:
        if not yt_link:
            return JSONResponse({"error": "YouTube link is required"})

        try :
            video_id = extract_video_id(yt_link)
        except Exception as e:
            return {"error": str("Could not retrieve a transcript for the video YT API")}

        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        formatter = TextFormatter()

        text_formatted = formatter.format_transcript(transcript)

        content = (
            f"Instruction: You are a YouTube summary generator, your job is to generate a summary of the given data. "
            f"You have to follow the instructions given on how to generate the summary. If no instruction is given, "
            f"then just generate the summary. Data: {transcript} & UserPrompt: {userPrompt} "
            f"Instruction: The summary should be at least 200 words long."
        )

        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": content}],
            model="llama3-70b-8192",
        )

        return chat_completion.choices[0].message.content
    except Exception as e:
        print(e)
        return {"error": str(e)}

@app.post("/ytchat")
async def file_chat(
    yt_link: Annotated[str, Form()] = None,
    userPrompt: Annotated[str, Form()] = None):
    try:
        print(yt_link)
        print(userPrompt)
        if not yt_link:
            return JSONResponse({"error": "YouTube link is required"})

        try:
            video_id = extract_video_id(yt_link)
        except Exception as e:
            return {"error": str("Could not retrieve a transcript for the video")}

        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        formatter = TextFormatter()

        text_formatted = formatter.format_transcript(transcript)

        store = DocumentStore()
        
        store.add_document(text_formatted)

        if not userPrompt:
            userPrompt = ""

        relevant_chunks = store.query(userPrompt, top_k=5)
        combined_text = " ".join(relevant_chunks)

        content = (
            f"Role: You are the Q&A solver. Here is your information: Data: {combined_text} "
            f"Using this information, answer the following question: Question: {userPrompt} "
            f"Instruction: Answer the question using the information provided in the data."
        )

        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": content}],
            model="llama3-70b-8192",
        )

        # Return the chat completion result
        print(chat_completion.choices[0].message.content)
        return chat_completion.choices[0].message.content
    
    except Exception as e:
        print(e)
        return JSONResponse({"error": str(e)})

@app.post("/ytquiz")
async def quiz(
    yt_link: Annotated[str, Form()] = None,
    userPrompt: Annotated[str, Form()] = None):
    try:
        if not yt_link:
            return JSONResponse({"error": "YouTube link is required"})

        try:
            video_id = extract_video_id(yt_link)
        except Exception as e:
            return {"error": str("Could not retrieve a transcript for the video YT API")}

        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        formatter = TextFormatter()

        text_formatted = formatter.format_transcript(transcript)

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,
            length_function=len,
            is_separator_regex=False,
        )

        chunk = text_splitter.create_documents([text_formatted])

        combined_text = ""
        for i in range(4):
            combined_text += str(random.choice(chunk))


        content = (
            f"Generate a quiz based on the following information: Data: {combined_text} "
            f"Instructions :"
            f"1. Generate a quiz based on the given information."
            f"2. The quiz should be at least 10 questions long."
            f"3. The quiz should be in the form of a list of questions and options."
            f"Format of the quiz:"
            f"Each question should be start with **Question :***"
            f"Option should be start with **Option :***"
            f"Each answer should be like **Answer :*** and only give the option number for the answer"
            f"Options: 1, 2, 3, 4"
            f"Answer: Answer"
        ) 

        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": content}],
            model="llama3-70b-8192",
        )

        
        def parse_quiz(response):
            question_blocks = re.split(r"\*\*Question \d+:\*\*", response)[1:]
            parsed_quiz = []

            for block in question_blocks:
                question_match = re.search(r"^(.*?)\n", block)
                question_text = question_match.group(1).strip() if question_match else block.strip()
                
                options = re.findall(r"\*\*Option (\d+):\*\* (.*?)\n", block)
                formatted_options = [f"{opt[1]}" for opt in options]

                answer_match = re.search(r"\*\*Answer:\*\* (\d+)", block)
                answer_option = answer_match.group(1) if answer_match else ""

                parsed_quiz.append({
                    "question": question_text,
                    "options": formatted_options,
                    "answer": answer_option
                })

            return parsed_quiz

        
        print(chat_completion.choices[0].message.content)
        json_format =  parse_quiz(chat_completion.choices[0].message.content) 
        print(json_format)

        json_format = json.dumps(json_format)
        print(json_format)

        json_compatible_item_data = jsonable_encoder(json_format)
        print(json_compatible_item_data)

        return JSONResponse(content=json_compatible_item_data)

    except Exception as e:
        print(e)
        return {"error": str("Could not retrieve a transcript for the video")}

@app.post("/v2/ytquiz")
async def v2YTquiz(
    item : YTTranscript):
    try: 
        print(item)
        yt_link = item.yt_link
        if not yt_link:
            return JSONResponse({"error": "YouTube link is required"})
        print(yt_link)

        try:
            video_id = extract_video_id(yt_link)
        except Exception as e:
            return {"error": str("Could not retrieve a transcript for the video YT API")}

        try : 
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            formatter = TextFormatter()
        except Exception as e:
            transcript = False

        if transcript == False:
            print("No transcript found")
            content = (
                f"Generate a quiz based on the give Topic : Topic: {item.title} "
                f"Instructions :"
                f"1. Generate a quiz based on the given information."
                f"2. The quiz should be at least 10 questions long."
                f"3. The quiz should be in the form of a list of questions and options."
                f"Format of the quiz:"
                f"Each question should be start with **Question :***"
                f"Option should be start with **Option :***"
                f"Each answer should be like **Answer :*** and only give the option number for the answer"
                f"Options: 1, 2, 3, 4"
                f"Answer: Answer"
            ) 

            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": content}],
                model="llama3-70b-8192",
            )
        else:
            print("Transcript found")
            print(transcript)
            text_formatted = formatter.format_transcript(transcript)

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=2000,
                length_function=len,
                is_separator_regex=False,
            )

            chunk = text_splitter.create_documents([text_formatted])

            combined_text = ""
            for i in range(4):
                combined_text += str(random.choice(chunk))

            content = (
                f"Generate a quiz based on the following information: Data: {combined_text} "
                f"Instructions :"
                f"1. Generate a quiz based on the given information."
                f"2. The quiz should be at least 10 questions long."
                f"3. The quiz should be in the form of a list of questions and options."
                f"Format of the quiz:"
                f"Each question should be start with **Question :***"
                f"Option should be start with **Option :***"
                f"Each answer should be like **Answer :*** and only give the option number for the answer"
                f"Options: 1, 2, 3, 4"
                f"Answer: Answer"
            ) 

            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": content}],
                model="llama3-70b-8192",
            )
        
        def parse_quiz(response):
            question_blocks = re.split(r"\*\*Question \d+:\*\*", response)[1:]
            parsed_quiz = []

            for block in question_blocks:
                question_match = re.search(r"^(.*?)\n", block)
                question_text = question_match.group(1).strip() if question_match else block.strip()
                
                options = re.findall(r"\*\*Option (\d+):\*\* (.*?)\n", block)
                formatted_options = [f"{opt[1]}" for opt in options]

                answer_match = re.search(r"\*\*Answer:\*\* (\d+)", block)
                answer_option = answer_match.group(1) if answer_match else ""

                parsed_quiz.append({
                    "question": question_text,
                    "options": formatted_options,
                    "answer": answer_option
                })

            return parsed_quiz

        
        print(chat_completion.choices[0].message.content)
        json_format =  parse_quiz(chat_completion.choices[0].message.content) 

        json_format = json.dumps(json_format)

        json_compatible_item_data = jsonable_encoder(json_format)
        print(json_compatible_item_data)

        return JSONResponse(content=json_compatible_item_data)

    except Exception as e:
        print(e)
        return {"error": str("Could not retrieve a transcript for the video")}

@app.post("/v2/ytsummarize")
async def v2YTsummarize(
    item : YTTranscript):
    try: 
        print(item)
        yt_link = item.yt_link
        if not yt_link:
            return JSONResponse({"error": "YouTube link is required"})
        print(yt_link)

        try:
            video_id = extract_video_id(yt_link)
        except Exception as e:
            return {"error": str("Could not retrieve a transcript for the video YT API")}

        try : 
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            formatter = TextFormatter()
        except Exception as e:
            transcript = False

        if transcript == False:
            print("No transcript found")
            content = (
                f"Instruction: You are a YouTube summary generator, your job is to generate a summary of the given data. "
                f"You have to follow the instructions given on how to generate the summary. If no instruction is given, "
                f"then just generate the summary on the topic : Topic: {item.title} "
                f"Instruction: The summary should be at least 200 words long and formatted as follows:\n\n"
                f"<h2>Summary of {item.title}</h2>\n\n"
                f"<p>Summary text goes here, based on the provided data.</p>\n\n"
                f"<ul>\n"
                f"  <li>First key point</li>\n"
                f"  <li>Second key point</li>\n"
                f"  <li>Third key point</li>\n"
                f"  <li>...</li>\n"
                f"</ul>\n\n"
                f"<p>Additional summary text or concluding remarks.</p>\n\n"
                f"<p>Ready to test your knowledge? Take the quiz now and earn coins and XP!</p>"
            )

            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": content}],
                model="llama3-70b-8192",
            )
        else:
            print("Transcript found")
            print(transcript)
            text_formatted = formatter.format_transcript(transcript)

            content = (
                f"Instruction: You are a YouTube summary generator, your job is to generate a summary of the given data. "
                f"You have to follow the instructions given on how to generate the summary. If no instruction is given, "
                f"then just generate the summary. Data: {text_formatted} "
                f"Instruction: The summary should be at least 200 words long and formatted as follows:\n\n"
                f"<h2>Summary of {item.title}</h2>\n\n"
                f"<p>Summary text goes here, based on the provided data.</p>\n\n"
                f"<ul>\n"
                f"  <li>First key point</li>\n"
                f"  <li>Second key point</li>\n"
                f"  <li>Third key point</li>\n"
                f"  <li>...</li>\n"
                f"</ul>\n\n"
                f"<p>Additional summary text or concluding remarks.</p>\n\n"
                f"<p>Ready to test your knowledge? Take the quiz now and earn coins and XP!</p>"
            )

            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": content}],
                model="llama3-70b-8192",
            )
        

        json_compatible_item_data = jsonable_encoder(chat_completion.choices[0].message.content)
        print(json_compatible_item_data)

        return JSONResponse(content=json_compatible_item_data)

    except Exception as e:
        print(e)
        return {"error": str("Could not retrieve a transcript for the video")}

@app.post("/v2/ytQuizAndSummary")
async def v2YTQuizAndSummary(
    item : YTTranscript) :
    try:
        print(item)
        yt_link = item.yt_link
        if not yt_link:
            return JSONResponse({"error": "YouTube link is required"})
        print(yt_link)

        try:
            video_id = extract_video_id(yt_link)
        except Exception as e:
            return {"error": str("Could not retrieve a transcript for the video YT API")}

        try : 
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            formatter = TextFormatter()
        except Exception as e:
            transcript = False

        if transcript == False:
            print("No transcript found")
            content = (
                f"Instruction: You are a YouTube summary generator, your job is to generate a summary of the given data. "
                f"You have to follow the instructions given on how to generate the summary. If no instruction is given, "
                f"then just generate the summary on the topic : Topic: {item.title} "
                f"Instruction: The summary should be at least 200 words long and formatted as follows:\n\n"
                f"<h2>Summary of {item.title}</h2>\n\n"
                f"<p>Summary text goes here, based on the provided data.</p>\n\n"
                f"<ul>\n"
                f"  <li>First key point</li>\n"
                f"  <li>Second key point</li>\n"
                f"  <li>Third key point</li>\n"
                f"  <li>...</li>\n"
                f"</ul>\n\n"
                f"<p>Additional summary text or concluding remarks.</p>\n\n"
                f"<p>Ready to test your knowledge? Take the quiz now and earn coins and XP!</p>"
            )

            summery_response = client.chat.completions.create(
                messages=[{"role": "user", "content": content}],
                model="llama3-70b-8192",
            )
        else:
            print("Transcript found")
            print(transcript)
            text_formatted = formatter.format_transcript(transcript)

            content = (
                f"Instruction: You are a YouTube summary generator, your job is to generate a summary of the given data. "
                f"You have to follow the instructions given on how to generate the summary. If no instruction is given, "
                f"then just generate the summary. Data: {text_formatted} "
                f"Instruction: The summary should be at least 200 words long and formatted as follows:\n\n"
                f"<h2>Summary of {item.title}</h2>\n\n"
                f"<p>Summary text goes here, based on the provided data.</p>\n\n"
                f"<ul>\n"
                f"  <li>First key point</li>\n"
                f"  <li>Second key point</li>\n"
                f"  <li>Third key point</li>\n"
                f"  <li>...</li>\n"
                f"</ul>\n\n"
                f"<p>Additional summary text or concluding remarks.</p>\n\n"
                f"<p>Ready to test your knowledge? Take the quiz now and earn coins and XP!</p>"
            )

            summery_response = client.chat.completions.create(
                messages=[{"role": "user", "content": content}],
                model="llama3-70b-8192",
            )

        content = (
            f"Generate a quiz based on the following information: Data: {summery_response.choices[0].message.content} "
            f"Instructions :"
            f"1. Generate a quiz based on the given information."
            f"2. The quiz should be at least 10 questions long."
            f"3. The quiz should be in the form of a list of questions and options."
            f"Format of the quiz:"
            f"Each question should be start with **Question :***"
            f"Option should be start with **Option :***"
            f"Each answer should be like **Answer :*** and only give the option number for the answer"
            f"Options: 1, 2, 3, 4"
            f"Answer: Answer"
        ) 

        quiz_response = client.chat.completions.create(
            messages=[{"role": "user", "content": content}],
            model="llama3-70b-8192",
        )

        print(quiz_response.choices[0].message.content)
        json_format =  parse_quiz(quiz_response.choices[0].message.content)

        json_format = json.dumps(json_format)

        json_compatible_item_data = jsonable_encoder({
            "summery" : summery_response.choices[0].message.content,
            "quiz" : json_format
        })

        print(json_compatible_item_data)

        return JSONResponse(content=json_compatible_item_data)
    except Exception as e:
        print(e)
        return {"error": str("Could not retrieve a transcript for the video")}