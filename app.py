from flask import Flask, render_template, request, redirect, url_for
import requests
import json

app = Flask(__name__)

# Replace with your OpenRouter API key
OPENROUTER_API_KEY = 'your-own-api-key'

# Load professor data from the JSON file
def load_professors():
    try:
        with open('professors.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

professors = load_professors()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('query')
    if not query:
        return redirect(url_for('index'))

    # Prepare the AI query including the professor data
    prompt = (
        f"Find a professor who matches this criteria: {query}. Here is the data:\n"
        f"{json.dumps(professors, indent=2)}"
    )

    # Make a request to OpenRouter API
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "meta-llama/llama-3.1-8b-instruct:free",
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
        )
        response.raise_for_status()  # Raise an HTTPError for bad responses

        data = response.json()
        if 'choices' in data and len(data['choices']) > 0:
            message = data['choices'][0]['message']['content']
            return render_template('results.html', message=message)
        else:
            return "No relevant results found.", 404
    except requests.RequestException as e:
        return f"Error fetching data from OpenRouter API: {e}", 500

if __name__ == '__main__':
    app.run(debug=True)
