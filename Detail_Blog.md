# Creating the Summarize the PDF Application

**Project Name:** PDF to Summary

**URL:** https://summarizer-aigurukul.vercel.app/

## Choosing the Tech Stack

Selecting the right tech stack is crucial. We need to consider various factors to ensure we make the best choice. For this project, we need to make API requests to the server and integrate the Gorq SDK.

## Choosing the Backend Framework

The primary task for the backend is to design a simple API server that accepts requests, processes them, and returns responses. This can be accomplished using several technologies such as JavaScript (NodeJS), Python (Flask, FastAPI), Java (Spring Boot), Go, and more. However, since the Gorq SDK is available only in JavaScript and Python, we need to choose between these two languages.

Considering the maturity and extensive use of Python in the AI and ML community, along with its robust library and tool support, I decided to use Python. JavaScript, while powerful, is relatively new in the AI/ML space and not as widely adopted by data scientists and ML engineers.

Python offers two widely used API development frameworks: Flask and FastAPI. Choosing between them requires a close examination of their capabilities. Flask is built for synchronous processing, while FastAPI supports both synchronous and asynchronous processing, allowing it to handle requests sequentially, concurrently, and in parallel. Given our need for asynchronous behavior to make API calls using the Gorq SDK, FastAPI is the best choice.

Thus, we chose Python as the backend language and FastAPI as the framework after considering the project's requirements and the features of each option.

## Choosing the Frontend Framework

For the frontend, we need a framework that is widely used, has a large community, and is easy to deploy. Next.js (based on ReactJS) fits these criteria perfectly. It offers extensive library support, including libraries for PDF to text conversion, Shadcn (UI library), Tailwind CSS, and built-in routing, making it a suitable choice for our project.

## Deployment

After creating the project within two days, it was time for deployment. We needed a free service with minimal requirements for hosting our server code. After some research, I chose Railway because of my familiarity with its deployment process. Deployment on Railway is straightforward; it requires adding the necessary libraries to the `requirements.txt` file and configuring the deployment in the `railway.json` file.

For the frontend, Next.js, we chose Vercel, the most reliable and popular hosting platform for this framework. Deployment on Vercel is simple, and within a few clicks, everything was live. The application worked perfectly in the local environment.

However, when we shared the application URL, about 60% of users reported issues: they were not getting responses from the backend server, the app was stuck on the loading screen, and then it returned to the main screen. This was puzzling because it worked fine for me and some others.

I searched extensively for solutions, consulted multiple Stack Overflow threads, and read the official documentation, but nothing resolved the issue. I even experimented with CORS settings, allowing specific URLs and using the wildcard [*] to accept all requests, but the issue persisted.

Eventually, I realized that the requests were being blocked by the browser, not the server. This might be due to Railway's free trial resources potentially being used for malicious activities, causing browsers to block the requests.

Therefore, I switched to another free platform, Render. Similar to Railway, Render requires adding a `render.yaml` file for configuration. After deploying the server on Render and updating the frontend URL, the application worked flawlessly. I asked the users who previously reported issues to test again, and they all responded positively.

Below, I will link all the documentation, articles, and videos that were instrumental in building this project.

 CORS (Cross-Origin Resource Sharing) : [Docs Link](https://fastapi.tiangolo.com/tutorial/cors/)

Fast Api Docs : [Docs link](https://fastapi.tiangolo.com/tutorial/)

How FastAPI Handles Requests Behind the Scenes : [Video link](https://www.youtube.com/watch?v=tGD3653BrZ8)

Why You NEED To Learn FastAPI | Hands On Project : [Video link](https://www.youtube.com/watch?v=cbASjoZZGIw)