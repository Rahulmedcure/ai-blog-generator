from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import fitz  # PyMuPDF
import openai

# --- WARNING: Hardcoding API keys is insecure in production ---
import os
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
CORS(app)

HTML_TEMPLATE = """
<!doctype html>
<html>
<head><title>Upload PDF to Generate Blog</title></head>
<body>
  <h2>Upload PDF to Generate Blog</h2>
  <form action="/generate" method="post" enctype="multipart/form-data">
    <input type="file" name="pdf_file" required>
    <input type="submit" value="Generate Blog">
  </form>
  <h3>Blog Output:</h3>
  <div style="white-space: pre-wrap; border: 1px solid gray; padding: 10px;">{{ blog }}</div>
</body>
</html>
"""

def extract_text_from_pdf(file_stream):
    pdf_doc = fitz.open(stream=file_stream.read(), filetype="pdf")
    text = ""
    for page in pdf_doc:
        text += page.get_text()
    return text

def call_gpt(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a blog writer. Write a human-friendly blog from the given PDF text."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=800
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"Error calling OpenAI API:\n\n{str(e)}"

@app.route('/', methods=['GET'])
def home():
    return render_template_string(HTML_TEMPLATE, blog="")

@app.route('/generate', methods=['POST'])
def generate_blog():
    if 'pdf_file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    pdf_file = request.files['pdf_file']
    if pdf_file.filename == '':
        return jsonify({"error": "Empty filename"}), 400

    try:
        raw_text = extract_text_from_pdf(pdf_file)
        blog_output = call_gpt(raw_text)
        return render_template_string(HTML_TEMPLATE, blog=blog_output)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
