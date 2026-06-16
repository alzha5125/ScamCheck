from flask import Flask, request, render_template
from google import genai

client = genai.Client(api_key="")

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():

    scam = request.form.get('message')

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=f"""
        Bạn là chuyên gia phát hiện lừa đảo.
        Phân tích tin nhắn sau:
        {scam}
        không thêm format cho văn bản, giữ nó dưới dạng một tin nhắn vừa phải
        """
    )

    return response.text

if __name__ == '__main__':
    app.run(debug=True)
