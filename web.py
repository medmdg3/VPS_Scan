from flask import Flask, jsonify, request
from OCR import scan

from OCR import reader
import cv2
import json
import numpy as np
app = Flask(__name__)

@app.route('/api', methods=['POST'])
def api():
    image = None
    image_file = request.files['image'].read()  # Read the image as bytes
    # Convert the byte data to a numpy array
    np_image = np.frombuffer(image_file, np.uint8)
    # Decode the numpy array as an image
    image = cv2.imdecode(np_image, cv2.IMREAD_COLOR)
    Type=request.form.get('Type')
    Reponse = scan(Type=Type,Image=image)
    return Reponse

if __name__ == '__main__':
    app.run(debug=True)
