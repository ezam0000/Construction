import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from openai import OpenAI
import base64
import logging

app = Flask(__name__, static_folder='build', static_url_path='')
CORS(app)

# Set up logging
logging.basicConfig(level=logging.INFO)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route('/analyze', methods=['POST'])
def analyze_image():
    try:
        if 'image_url' in request.form:
            image_url = request.form['image_url']
        elif 'image' in request.files:
            file = request.files['image']
            file_content = file.read()
            base64_image = base64.b64encode(file_content).decode('utf-8')
            image_url = f"data:image/jpeg;base64,{base64_image}"
        else:
            return jsonify({"error": "No image provided"}), 400

        system_message = "You are an expert in construction inspection and property appraisal. Analyze the provided image with a focus on professional assessment, safety concerns, and regulatory compliance. Provide a detailed, objective report suitable for official documentation."

        response = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {"role": "system", "content": system_message},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Conduct a detailed analysis of this construction or property image. Identify key elements, potential issues, and notable features relevant to a professional inspection or appraisal. Include observations on structural components, materials used, condition of visible elements, and any apparent code compliance concerns."},
                        {
                            "type": "image_url",
                            "image_url": {"url": image_url},
                        },
                    ],
                }
            ],
            max_tokens=500,
        )
        result = response.choices[0].message.content
        return jsonify({"result": result})
    except Exception as e:
        app.logger.error(f"An error occurred: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/test', methods=['GET'])
def test():
    return jsonify({"message": "Backend is working"})

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    app.logger.info(f"Requested path: {path}")
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        app.logger.info(f"Serving index.html for path: {path}")
        return send_from_directory(app.static_folder, 'index.html')

@app.errorhandler(404)
def not_found(e):
    app.logger.error(f"404 error: {e}")
    return jsonify(error=str(e)), 404

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
