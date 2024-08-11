from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file:
        response = client.files.create(
            file=file,
            purpose='assistants'
        )
        return jsonify({"file_id": response.id})

@app.route('/analyze', methods=['POST'])
def analyze_image():
    try:
        data = request.json
        messages = [{"role": "user", "content": "What's in this image?"}]
        
        if data.get('image_url'):
            messages[0]["content"] = [
                {"type": "text", "text": "What's in this image?"},
                {"type": "image_url", "image_url": {"url": data['image_url']}}
            ]
        elif data.get('file_id'):
            messages[0]["content"] = [
                {"type": "text", "text": "What's in this image?"},
                {"type": "image_file", "image_file": {"file_id": data['file_id']}}
            ]
        else:
            return jsonify({"error": "No image URL or file provided"}), 400

        response = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=messages,
            max_tokens=300
        )
        return jsonify({"result": response.choices[0].message.content})
    except Exception as e:
        app.logger.error(f"An error occurred: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/test', methods=['GET'])
def test():
    return jsonify({"message": "Backend is working"})

if __name__ == '__main__':
    app.run(debug=True)
