import os
import pdfplumber
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
                if page_text:  # Check if text was extracted successfully
                    text += page_text + "\n\n"
            
            if not text.strip():
                return None, "The PDF appears to be scanned or has no extractable text."
            
            return text, None
    except Exception as e:
        return None, f"Error extracting text from PDF: {e}"

def analyze_resume(pdf_path):
    """Extract text from a resume PDF and analyze it with GPT-4o."""
    print(f"Analyzing resume: {pdf_path}")
    
    # Extract text from the PDF
    resume_text, error = extract_text_from_pdf(pdf_path)
    
    if error:
        print(error)
        return None
    
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
    
    print("\n--- Resume Analysis ---\n")
    print(analysis)
    
    # Save the analysis to a file
    output_filename = os.path.splitext(os.path.basename(pdf_path))[0] + "_analysis.txt"
    with open(output_filename, "w") as file:
        file.write(analysis)
    
    print(f"\nAnalysis saved to {output_filename}")
    return analysis

# Main execution - can be used from command line
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python resume_analyzer.py path/to/resume.pdf")
    else:
        pdf_path = sys.argv[1]
        if not os.path.exists(pdf_path):
            print(f"Error: File {pdf_path} not found.")
        else:
            analyze_resume(pdf_path)
