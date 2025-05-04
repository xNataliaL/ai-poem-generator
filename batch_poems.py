import os
from dotenv import load_dotenv
import openai
import datetime

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

def generate_poem_for_name(name):
    """Generate and save a poem for a given name."""
    prompt = f"""Write a 4 line rhyming poem on {name}'s excellent coding skills. 
    Make the poem upbeat, encouraging and humorous."""
    
    poem = get_response_to_prompt(prompt)
    
    # Create a batch_poems directory if it doesn't exist
    if not os.path.exists("batch_poems"):
        os.makedirs("batch_poems")
    
    # Save the poem to an individual file
    filename = f"batch_poems/{name.lower()}_poem.txt"
    with open(filename, "w") as file:
        file.write(f"Poem for {name} - {datetime.datetime.now()}:\n{poem}")
    
    print(f"Generated poem for {name} and saved to {filename}")
    return poem

def process_names_file(filename):
    """Read names from a file and generate poems for each one."""
    try:
        with open(filename, "r") as file:
            names = [line.strip() for line in file if line.strip()]
        
        print(f"Found {len(names)} names in {filename}")
        
        for name in names:
            generate_poem_for_name(name)
            
        print(f"Successfully generated {len(names)} poems!")
        
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
    except Exception as e:
        print(f"Error processing file: {e}")

# Run the batch process
if __name__ == "__main__":
    process_names_file("names.txt")