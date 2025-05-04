# AI Poem Generator 📝✨

This is a beginner-friendly AI-powered app that generates fun, 4-line poems based on people’s names — and even analyzes PDF resumes using GPT-4o. Built with Python and FastAPI, it stores results in MongoDB for easy access and persistence.

## Features

- 🧠 Generates personalized poems with GPT-4o  
- 📄 Analyzes resumes from uploaded PDF files  
- ☁️ Saves poem history to MongoDB Atlas  
- 💻 Simple web interface built with FastAPI  

## How to Set It Up (Windows)

1. Clone this repository to your computer  
2. Create a virtual environment:  
   ```
   python -m venv ai-env
   ```
3. Activate it:  
   ```
   ai-env\Scripts\activate
   ```
4. Install the required packages:  
   ```
   pip install fastapi uvicorn openai python-dotenv pymongo pdfplumber
   ```
5. Create a `.env` file in the project folder, and add your credentials:  
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   MONGO_URL=your_mongodb_connection_string_here
   ```
6. Run the poem app:  
   ```
   uvicorn poem:app --reload
   ```
7. Open your browser and go to [http://127.0.0.1:8000](http://127.0.0.1:8000)

## Files and Folders

- `poem.py` – Web app to generate poems  
- `resume_analyzer.py` – Script to extract and summarize resume content  
- `resume_app.py` – Web interface for uploading and analyzing resumes  
- `batch_poems.py` – Generates poems in bulk from a list of names  
- `.env` – Stores secret keys (make sure it's in your `.gitignore`)  
- `.gitignore` – Prevents sensitive or unnecessary files from being tracked  
- `README.md` – You're reading it 😉

## Note

This app is part of a learning journey using the **AI Builder: From Zero to AI-Powered Apps** course. It's not production-ready, but it’s a great foundation for real-world AI app development.

## License

🛠 For educational use only.
