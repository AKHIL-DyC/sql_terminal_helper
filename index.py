import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import requests

# Load environment variables from .env file
load_dotenv()
API_KEY = os.getenv("API_KEY")

app = Flask(__name__)

@app.route('/', methods=['GET'])
def generate_response():
    # Retrieve the 'prompt' from query parameters
    prompt = request.args.get('prompt')
    if not prompt:
        return jsonify({"error": "Please provide a prompt query parameter."}), 400

    try:
        # Modify the prompt to focus only on generating SQL queries
        sql_prompt = f"Generate the SQL query for the following task: {prompt}. Only provide the SQL query, no explanations."
        
        # Google Generative Language API endpoint
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={API_KEY}"
        
        # JSON payload for the request
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": sql_prompt}
                    ]
                }
            ]
        }
        
        # Send POST request to Google API
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, headers=headers, json=payload)
        
        # Check for errors in the response
        if response.status_code != 200:
            return jsonify({"error": f"Error generating content: {response.text}"}), response.status_code
        
        # Print the entire response for debugging purposes
        result = response.json()
        print(result)  # This will print the raw response to the console for debugging
        
        # Try to extract just the SQL query from the response
        if 'candidates' in result and len(result['candidates']) > 0:
            sql_query = result['candidates'][0]['content']['parts'][0]['text'].strip('```sql\n').strip('```')
            return jsonify({"sql_query": sql_query})
        else:
            return jsonify({"error": "No candidates found in the response."}), 500
        
    except Exception as e:
        return jsonify({"error": f"Error processing request: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
