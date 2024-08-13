import os
import base64
import logging
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from PIL import Image
from io import BytesIO
from openai import OpenAI

# Initialize Flask application
app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

# Set up logging
logging.basicConfig(level=logging.INFO)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Supported image formats
SUPPORTED_IMAGE_FORMATS = ('.png', '.jpg', '.jpeg', '.gif', '.webp')

@app.route('/analyze', methods=['POST'])
def analyze_image():
    """
    Analyzes an uploaded image or image URL and returns the analysis result.
    """
    app.logger.info("Received POST request on /analyze")
    
    try:
        messages = []

        # Check for image URL or uploaded files
        if 'image_url' in request.form:
            image_url = request.form['image_url']
            messages.append({
                "role": "user",
                "content": [
                    {"type": "text", "text": "What’s in this image?"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url,
                        }
                    }
                ]
            })
        elif 'image' in request.files:
            files = request.files.getlist('image')  # Support multiple file uploads
            
            for file in files:
                # Validate file size
                if file.content_length > 20 * 1024 * 1024:  # Limit to 20 MB
                    return jsonify({"error": "File size exceeds the limit of 20 MB."}), 400

                # Validate file format (case insensitive)
                if not file.filename.lower().endswith(SUPPORTED_IMAGE_FORMATS):
                    return jsonify({
                        "error": f"Unsupported image format. Please upload an image in one of the following formats: {', '.join(SUPPORTED_IMAGE_FORMATS)}."
                    }), 400
                
                # Open the image and check dimensions
                image = Image.open(file)
                width, height = image.size
                app.logger.info(f"Uploaded image dimensions: {width}x{height}")

                # Resize if necessary
                if width > 2000 or height > 2000:
                    # Resize the image to the maximum dimensions
                    image.thumbnail((2000, 2000), Image.LANCZOS)
                elif min(width, height) < 768:
                    # Resize to ensure the shortest side is at least 768px
                    if width < height:
                        image = image.resize((768, int((768 / width) * height)), Image.LANCZOS)
                    else:
                        image = image.resize((int((768 / height) * width), 768), Image.LANCZOS)

                # Encode the image content in base64
                buffer = BytesIO()
                image.save(buffer, format="JPEG")  # Save as JPEG format
                buffer.seek(0)
                file_content = buffer.read()
                base64_image = base64.b64encode(file_content).decode('utf-8')
                
                # Append the image data to messages
                messages.append({
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "What’s in this image?"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                })
        else:
            return jsonify({"error": "No image provided."}), 400

        # Prepare the system message for OpenAI analysis
        system_message = (
            "You are an expert in construction inspection and property appraisal. "
            "Analyze the provided image(s) with a focus on professional assessment, safety concerns, and regulatory compliance. "
            "Provide a detailed, objective report suitable for official documentation."
        )

        # Call OpenAI API with the prepared messages
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_message},
                *messages  # Unpack messages for multiple images
            ],
            max_tokens=300,
        )

        # Get the result from OpenAI response
        result = response.choices[0].message.content

        # Format the output for clarity
        formatted_output = format_output(result)

        return jsonify({"result": formatted_output})

    except Exception as e:
        app.logger.error(f"An error occurred: {str(e)}")
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

def format_output(result):
    """
    Format the output for better readability.
    This function can be customized to parse the result and extract key information.
    """
    # Example of basic formatting - this can be customized as needed
    formatted_result = result.strip().replace("\n", "<br>")  # Replace newlines with HTML line breaks
    return formatted_result

@app.route('/test', methods=['GET'])
def test():
    """
    Test endpoint to check if the backend is working.
    """
    return jsonify({"message": "Backend is working!"})

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """
    Serve the index.html file or other static files.
    """
    app.logger.info(f"Requested path: {path}")
    
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        app.logger.info("Serving index.html")
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    # Use the PORT environment variable for Heroku
    port = int(os.environ.get("PORT", 5002))
    app.run(host='0.0.0.0', port=port)
