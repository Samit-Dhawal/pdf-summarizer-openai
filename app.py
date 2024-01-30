import os
import openai
from flask import Flask, request, render_template
from pdfminer.high_level import extract_text

app = Flask(__name__)

# Setting OpenAI API key
openai.api_key = 'YOUR_API_KEY'

# Setting a limit on the number of requests per minute to avoid exceeding rate limits
RATE_LIMIT = 5  # Can adjust this value based on OpenAI plan

# Creating a 'pdfs' directory to store uploaded PDFs if it doesn't exist
if not os.path.exists('pdfs'):
    os.makedirs('pdfs')

def extract_text_from_pdf(pdf_file_path):
    try:
        text = extract_text(pdf_file_path)
        print(text)
        return text
    
    except Exception as e:
        print(f'Error extracting text from PDF: {str(e)}')
        return None

def ask_question(question, context):
    response = openai.Completion.create(
        engine="text-davinci-001",
        prompt=f"Answer the following question:\nQ: {question}\nContext: {context}\nAnswer:",
        max_tokens=50,  # Adjust max tokens as needed
    )
    return response.choices[0].text

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        uploaded_pdf = request.files['pdf']
        question = request.form['question']
        if uploaded_pdf and question:
            # Saving the uploaded PDF to the 'pdfs' directory
            pdf_file_path = os.path.join('pdfs', uploaded_pdf.filename)
            uploaded_pdf.save(pdf_file_path)

            # Extracting text from the saved PDF
            pdf_text = extract_text_from_pdf(pdf_file_path)

            # Using OpenAI GPT-3.5 for question answering, with rate limiting
            if pdf_text:
                try:
                    answer = ask_question(question, pdf_text)
                    return render_template('index.html', answer=answer, text=pdf_text)
                except openai.error.RateLimitError:
                    return render_template('index.html', answer="Rate limit exceeded. Please try again later.", text=pdf_text)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)