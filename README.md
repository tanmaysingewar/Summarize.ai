# Summarize.ai
# Title: PDF to Summary Documentation

## Project Overview

**Project Name:** PDF to Summary

**URL:** https://summarizer-aigurukul.vercel.app/

PDF to Summary is a web application that allows users to upload PDF files and receive a concise summary of their content. This documentation provides a detailed guide on the project's structure, tech stack, deployment process, and usage instructions.

# New Feature  Added
### Quiz Generator : You can now generate quiz based on the uploaded pdf file

- Just upload the pdf file and click on generate quiz button and you will get the quiz
- You can also solve the quiz and get the marks


## Tech Stack

### Backend

- **Language:** Python
- **Framework:** FastAPI
- **SDK:** Gorq SDK 
- **Modal:** Mixtral 8x7b Model  

### Frontend

- **Framework:** Next.js (based on ReactJS)
- **Libraries:**
    - Shadcn (UI library)
    - Tailwind CSS

### Deployment

- **Backend:** Render
- **Frontend:** Vercel

## Project Structure

### Backend (FastAPI)

1. **Main Application File:** `main.py`
    - Contains the FastAPI app initialization, route definitions, and Gorq SDK integration.
2. **Routes:**
    - `/health`: Endpoint to check the health of the Application.
    - `/summary`: Endpoint to return the summary of the uploaded PDF.
    - `/chat`: Endpoint can chat with the model.
3. **Dependencies:**
    - `requirements.txt`: Lists all Python dependencies.
    - `render.yaml`: Configuration file for deploying on Render.

### Frontend (Next.js)

1. **Pages:**
    - `page.js`: Main landing page where users can log In to the Application.
    - `dashboard/page.js`: Page to display the main interface of the application.
2. **Components:**
    - `UI`: Component for shadcn UI elements.
3. **Styles:**
    - Tailwind CSS for styling.

## Deployment Guide

### Backend Deployment (Render)

1. **Create Render Account:** Sign up at [Render](https://render.com/).
2. **Add Project:**
    - Connect your GitHub repository containing the backend code.
3. **Configuration:**
    - Ensure `requirements.txt` is present for dependencies.
    - Add `render.yaml` for deployment configuration.
4. **Deploy:**
    - Follow the prompts on Render to deploy the backend server.

### Frontend Deployment (Vercel)

1. **Create Vercel Account:** Sign up at [Vercel](https://vercel.com/).
2. **Add Project:**
    - Connect your GitHub repository containing the frontend code.
3. **Configuration:**
    - Ensure `next.config.js` is properly set up.
    - Deploy directly from the Vercel dashboard.
4. **Deploy:**
    - Follow the prompts on Vercel to deploy the front end.

## Usage Instructions

1. **Access the Application:**
    - Go to https://summarizer-aigurukul.vercel.app/.
2. **Upload a PDF:**
    - On the main page, use the upload form to select and upload a PDF file.
3. **Get the Summary:**
    - After uploading, the application processes the PDF and displays a summary on the page.

## Troubleshooting

### Common Issues and Solutions

1. **Backend Server Not Responding:**
    - Ensure the backend server on Render is running.
    - Check network requests in the browser's developer tools for errors.
2. **CORS Issues:**
    - Verify CORS settings in FastAPI.
    - Ensure the frontend is correctly configured to make requests to the backend.
3. **Deployment Errors:**
    - Check deployment logs on Render and Vercel for error messages.
    - Ensure all dependencies are listed in `requirements.txt` (backend) and `package.json` (frontend).

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Gorq SDK Documentation](https://gorq.io/docs)
- [Render Deployment Guide](https://render.com/docs)
- [Vercel Deployment Guide](https://vercel.com/docs)

## Conclusion

PDF to Summary is a robust application designed to simplify the process of extracting summaries from PDF documents. By leveraging FastAPI for the backend and Next.js for the front end, the application provides a seamless user experience. Deployment on Render and Vercel ensures that the application is scalable and easy to manage. This documentation serves as a comprehensive guide to understanding, deploying, and using the application effectively.