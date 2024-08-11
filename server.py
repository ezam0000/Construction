from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os
import base64
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

@app.route('/analyze', methods=['POST'])
def analyze_image():
    try:
        data = request.json
        response = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=data['messages'],
            max_tokens=data['max_tokens']
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
