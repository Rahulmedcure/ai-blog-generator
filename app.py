from flask import Flask, request, jsonify
from flask_cors import CORS
import fitz  # PyMuPDF
import openai
import os

# Set your OpenAI API key from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
CORS(app)  # Enable CORS for all domains

# Function to extract text from uploaded PDF
def extract_text_from_pdf(file_stream):
    pdf_doc = fitz.open(stream=file_stream.read(), filetype="pdf")
    text = ""
    for page in pdf_doc:
        text += page.get_text()
    return text

# Function to call OpenAI and generate blog content
def call_gpt(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a blog writer. Write a human-friendly blog from the given research paper text."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"Error calling OpenAI API:\n\n{str(e)}"

# Health check route
@app.route('/', methods=['GET'])
def home():
    return "✅ Blog Generator API is live. Use POST /generate with PDF upload."

# Main blog generation route
@app.route('/generate', methods=['POST'])
def generate_blog():
    if 'pdf_file' not in request.files:
        return jsonify({"error": "No PDF file uploaded"}), 400

    pdf_file = request.files['pdf_file']
    if pdf_file.filename == '':
        return jsonify({"error": "Uploaded file has no filename"}), 400

    try:
        raw_text = extract_text_from_pdf(pdf_file)
        blog_output = call_gpt(raw_text)
        return jsonify({"blog": blog_output})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run the Flask app
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Default to port 5000
    app.run(host='0.0.0.0', port=port, debug=True)
