import os
from dotenv import load_dotenv
import openai
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from pymongo import MongoClient
import datetime

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize MongoDB client
mongo_client = MongoClient(os.getenv("MONGO_URL"))
db = mongo_client["poetry_db"]
poems_collection = db["poems"]

def get_response_to_prompt(prompt, model="gpt-4o"):
    """Send a prompt to OpenAI and get a response."""
    return client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    ).choices[0].message.content

# Create FastAPI app
app = FastAPI()

# HTML Form (same as before)
HTML_FORM = """<!doctype html>
<html>
<head>
    <title>AI Poem Generator</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 600px;
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
        input {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
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
        .poem {
            white-space: pre-wrap;
            background: #f9f9f9;
            padding: 20px;
            border-radius: 4px;
            border-left: 4px solid #0077ff;
            margin-top: 20px;
            font-family: Georgia, serif;
            line-height: 1.5;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th, td {
            padding: 10px;
            border: 1px solid #ddd;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
    </style>
</head>
<body>
    <h1>AI Poem Generator</h1>
    <form method="post">
        <div class="form-group">
            <label for="name">Your Name:</label>
            <input id="name" name="name" required>
        </div>
        <button type="submit">Generate Poem</button>
    </form>
    <p><a href="/history">View Poem History</a></p>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML_FORM

@app.post("/", response_class=HTMLResponse)
async def generate_poem(name: str = Form(...)):
    # Craft a prompt for the AI
    prompt = f"""Write a 4 line rhyming poem on {name}'s excellent coding skills. 
    Make the poem upbeat, encouraging and humorous."""
    
    # Get response from OpenAI
    poem = get_response_to_prompt(prompt)
    
    # Save to file (file-based persistence)
    with open("poems.txt", "a") as file:
        file.write(f"Poem for {name} - {datetime.datetime.now()}:\n{poem}\n\n")
    
    # Save to MongoDB (database persistence)
    poem_document = {
        "name": name,
        "poem": poem,
        "created_at": datetime.datetime.now()
    }
    poems_collection.insert_one(poem_document)
    
    # Return HTML with the poem
    return f"""<!doctype html>
    <html>
    <head>
        <title>Your Personalized Poem</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                line-height: 1.6;
            }}
            h1 {{
                color: #0077ff;
                font-size: 28px;
                margin-bottom: 20px;
            }}
            .poem {{
                white-space: pre-wrap;
                background: #f9f9f9;
                padding: 20px;
                border-radius: 4px;
                border-left: 4px solid #0077ff;
                margin-top: 20px;
                font-family: Georgia, serif;
                line-height: 1.5;
                color: #5500aa;
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
        <h1>A Poem for {name}</h1>
        <div class="poem">{poem}</div>
        <form method="get" action="/">
            <button type="submit">Create Another Poem</button>
        </form>
        <p><a href="/history">View All Poems</a></p>
    </body>
    </html>
    """

@app.get("/history", response_class=HTMLResponse)
async def poem_history():
    # Retrieve poems from MongoDB
    poems = list(poems_collection.find().sort("created_at", -1))
    
    # Build HTML for the history page
    poems_html = ""
    for poem in poems:
        created_at = poem.get("created_at", datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
        poems_html += f"""
        <tr>
            <td>{poem.get("name", "Unknown")}</td>
            <td style="white-space: pre-wrap">{poem.get("poem", "")}</td>
            <td>{created_at}</td>
        </tr>
        """
    
    return f"""<!doctype html>
    <html>
    <head>
        <title>Poem History</title>
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
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }}
            th, td {{
                padding: 10px;
                border: 1px solid #ddd;
                text-align: left;
                vertical-align: top;
            }}
            th {{
                background-color: #f2f2f2;
                font-weight: bold;
            }}
            a {{
                color: #0077ff;
                text-decoration: none;
            }}
            a:hover {{
                text-decoration: underline;
            }}
        </style>
    </head>
    <body>
        <h1>Poem History</h1>
        <p><a href="/">← Back to Generator</a></p>
        
        <table>
            <tr>
                <th>Name</th>
                <th>Poem</th>
                <th>Created At</th>
            </tr>
            {poems_html}
        </table>
    </body>
    </html>
    """

# Run the app with: uvicorn poem:app --reload