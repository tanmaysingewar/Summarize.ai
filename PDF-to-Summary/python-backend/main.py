from fastapi import FastAPI,File,UploadFile,Form
from pydantic import BaseModel
from typing_extensions import Annotated

import os
from groq import Groq
from fastapi.middleware.cors import CORSMiddleware

from docx import Document
from PyPDF2 import PdfReader
from pathlib import Path

UPLOAD_DIR = Path() / "upload"

client = Groq(
    api_key="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",
)

class Data(BaseModel):
    file : UploadFile
    userPrompt : str | None = None


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins= ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def read_root():
    print("Health Check")
    return {"status": "ok"}

    if docs.data == "":
        return {"error": "File is required"}
    else: 

        content = "Role: You are the Q&A solver. Here is your information: Data: " + docs.data + "Using this information, answer the following question: Question:"+ docs.userPrompt + "Instruction: Answer the question using the information provided in the data."
        try : 
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": content,
                    }
                ],
                model="llama3-8b-8192",
            )
            return chat_completion.choices[0].message.content
        except :
            return {"error": str(e)}


def extract_text_from_pdf(file_data):
    reader = PdfReader(file_path)
    number_of_pages = len(reader.pages)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    print(text)
    return text

def extract_text_from_docx(file_data):
    doc = Document(file_data)
    print("Docs File Read")
    para = doc.paragraphs
    text = ""
    for p in para:
        text += p.text
    print(text)
    return text

def extract_text_from_txt(file_data):
    with open(file_data, "r") as f:
        text = f.read()
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
        
        os.remove(file_path)

        content = (
            f"Instruction: You are a summary generator, your job is to generate a summary of the given data. "
            f"You have to follow the instructions given on how to generate the summary. If no instruction is given, "
            f"then just generate the summary. Data: {text} Instruction: {userPrompt} "
            f"Instruction: The summary should be at least 200 words long."
        )

        # Assuming client.chat.completions.create is defined elsewhere
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": content}],
            model="llama3-8b-8192",
        )

        return chat_completion.choices[0].message.content
    except Exception as e:
        return {"error": str(e)}


@app.post("/chat")
async def file_chat(
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
        
        os.remove(file_path)

        content = "Role: You are the Q&A solver. Here is your information: Data: " + text + "Using this information, answer the following question: Question:"+ userPrompt + "Instruction: Answer the question using the information provided in the data."

        # Assuming client.chat.completions.create is defined elsewhere
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": content}],
            model="mixtral-8x7b-32768",
        )

        return chat_completion.choices[0].message.content
    except Exception as e:
        return {"error": str(e)}
