
from pathlib import Path
import sys
import json
import numpy as np
from PIL import Image
from flask import Flask, render_template, request, jsonify
from tensorflow.keras.models import load_model

# Find the correct folder when running normally or as an EXE
if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys._MEIPASS)
else:
    BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR / "models" / "plant_disease_cnn.keras"
CLASSES_PATH = BASE_DIR / "models" / "class_names.json"

IMG_SIZE = (128, 128)
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

# Configure the Flask application
app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static")
)

app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024  # 8 MB

model = None
class_names = []


def load_artifacts():
    global model, class_names

    if MODEL_PATH.exists() and CLASSES_PATH.exists():
        model = load_model(MODEL_PATH)
        class_names = json.loads(
            CLASSES_PATH.read_text(encoding="utf-8")
        )
    else:
        print("ERROR: Model or class names file not found.")
        print("Expected model:", MODEL_PATH)
        print("Expected classes:", CLASSES_PATH)


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    if model is None:
        return jsonify(
            error="Model not found. Check the models folder."
        ), 503

    if "leaf_image" not in request.files:
        return jsonify(error="Choose a leaf image first."), 400

    file = request.files["leaf_image"]

    if not file.filename or not allowed_file(file.filename):
        return jsonify(
            error="Upload a JPG, JPEG, or PNG image."
        ), 400

    try:
        image = Image.open(file.stream).convert("RGB").resize(IMG_SIZE)
        arr = np.asarray(image, dtype=np.float32)

        probabilities = model.predict(
            np.expand_dims(arr, axis=0),
            verbose=0
        )[0]

        index = int(np.argmax(probabilities))
        confidence = float(probabilities[index]) * 100

        return jsonify(
            disease=class_names[index],
            confidence=round(confidence, 2),
            note=(
                "AI result only. Confirm with a local agricultural "
                "expert, especially before treatment."
            )
        )

    except Exception as error:
        print("Prediction error:", error)
        return jsonify(
            error="The image could not be processed. Try another JPG or PNG image."
        ), 400


load_artifacts()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

