import os
import pdfplumber
from dotenv import load_dotenv
import openai
import tempfile
import shutil
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

def get_response_to_prompt(prompt, model="gpt-4o"):
    """Send a prompt to OpenAI and get a response."""
    return client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    ).choices[0].message.content

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            # Extract text from each page and join together
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"
            
            if not text.strip():
                return None, "The PDF appears to be scanned or has no extractable text."
            
            return text, None
    except Exception as e:
        return None, f"Error extracting text from PDF: {e}"

def analyze_resume(pdf_path):
    """Extract text from a resume PDF and analyze it with GPT-4o."""
    # Extract text from the PDF
    resume_text, error = extract_text_from_pdf(pdf_path)
    
    if error:
        return f"Error: {error}"
    
    # Create a prompt for analysis
    prompt = f"""Below is a resume of a candidate. Read the resume carefully, then extract and provide:

1. NAME: (the candidate's full name)
2. EMAIL: (their email address if found, or "Not found" if not present)
3. SUMMARY: (2-3 sentences summarizing their qualifications, focusing on their technical skills and experience)
4. SKILLS: (list their top 5 technical skills based on the resume)
5. EXPERIENCE LEVEL: (junior, mid-level, senior, or executive based on years and depth of experience)

Resume text:
{resume_text}

Format your response exactly as requested above, with clear headings.
"""
    
    # Get analysis from OpenAI
    analysis = get_response_to_prompt(prompt)
    return analysis

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Resume Analyzer</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                line-height: 1.6;
            }
            h1 {
                color: #0077ff;
                font-size: 28px;
                margin-bottom: 20px;
            }
            .form-group {
                margin-bottom: 15px;
            }
            label {
                display: block;
                margin-bottom: 5px;
                font-weight: bold;
            }
            button {
                background: #0077ff;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 16px;
                border-radius: 4px;
                cursor: pointer;
            }
            button:hover {
                background: #0055cc;
            }
            .result {
                white-space: pre-wrap;
                background: #f9f9f9;
                padding: 20px;
                border-radius: 4px;
                border-left: 4px solid #0077ff;
                margin-top: 20px;
                font-family: monospace;
                line-height: 1.5;
            }
        </style>
    </head>
    <body>
        <h1>Resume Analyzer</h1>
        <p>Upload a resume in PDF format to analyze it with AI.</p>
        
        <form action="/analyze/" enctype="multipart/form-data" method="post">
            <div class="form-group">
                <label for="resume">Resume PDF:</label>
                <input type="file" name="resume" accept=".pdf" required>
            </div>
            <button type="submit">Analyze Resume</button>
        </form>
    </body>
    </html>
    """

@app.post("/analyze/", response_class=HTMLResponse)
async def analyze(resume: UploadFile = File(...)):
    # Create a temporary directory to store the uploaded file
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file_path = os.path.join(temp_dir, resume.filename)
        
        # Save the uploaded file to the temporary directory
        with open(temp_file_path, "wb") as f:
            shutil.copyfileobj(resume.file, f)
        
        # Analyze the resume
        analysis = analyze_resume(temp_file_path)
    
    # Return the analysis results
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Resume Analysis Results</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                line-height: 1.6;
            }}
            h1 {{
                color: #0077ff;
                font-size: 28px;
                margin-bottom: 20px;
            }}
            .result {{
                white-space: pre-wrap;
                background: #f9f9f9;
                padding: 20px;
                border-radius: 4px;
                border-left: 4px solid #0077ff;
                margin-top: 20px;
                font-family: monospace;
                line-height: 1.5;
            }}
            a {{
                color: #0077ff;
                text-decoration: none;
            }}
            a:hover {{
                text-decoration: underline;
            }}
            button {{
                background: #0077ff;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 16px;
                border-radius: 4px;
                cursor: pointer;
                margin-top: 20px;
            }}
            button:hover {{
                background: #0055cc;
            }}
        </style>
    </head>
    <body>
        <h1>Resume Analysis Results</h1>
        <div class="result">{analysis}</div>
        <a href="/" style="display: block; margin-top: 20px;">Analyze Another Resume</a>
    </body>
    </html>
    """

# Run with: uvicorn resume_app:app --reload