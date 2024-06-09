from fastapi import FastAPI
from pydantic import BaseModel
import os
from groq import Groq
from fastapi.middleware.cors import CORSMiddleware


client = Groq(
    api_key="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",
)

class Docs(BaseModel):
    data : str
    userPrompt : str | None = None

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.post("/summarize")
def create_item(docs: Docs):
    print(docs)

    if docs.data == "":
        return {"error": "File is required"}
    else:
        content = "Instruction : Your are the summery generator, your job is to generate the summery of the give data and also you get some additional input how you should generate the summery, if not give just generate summery. Data :"+docs.data + "And Additional input : " + docs.userPrompt + "dont give any explanation  like here is you summery or something like that just start with the summery. And summery should be at least of 200 words."

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
        except Exception as e:
            return {"error": str(e)}