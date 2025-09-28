import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename
from stegano import encrypt_message, decrypt_message, encode_message, decode_message
from utils import allowed_file
from PIL import Image

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

app = Flask(__name__)
app.secret_key = "supersecretkey"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/hide", methods=["GET", "POST"])
def hide():
    if request.method == "POST":
        if "image" not in request.files:
            flash("No file selected")
            return redirect(request.url)

        file = request.files["image"]
        message = request.form["message"]
        password = request.form["password"]

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)

            # Convert to PNG
            img = Image.open(filepath).convert("RGB")
            png_name = os.path.splitext(filename)[0] + "_clean.png"
            png_path = os.path.join(app.config["UPLOAD_FOLDER"], png_name)
            img.save(png_path, format="PNG")

            # Encrypt message
            encrypted_message = encrypt_message(message, password)

            # Output stego image
            stego_name = os.path.splitext(filename)[0] + "_stego.png"
            stego_path = os.path.join(app.config["UPLOAD_FOLDER"], stego_name)

            # Encode message into image
            encode_message(png_path, encrypted_message, stego_path)

            return render_template(
                "result.html",
                result="Message hidden successfully!",
                image=stego_name
            )

    return render_template("hide.html")


@app.route("/reveal", methods=["GET", "POST"])
def reveal():
    if request.method == "POST":
        if "image" not in request.files:
            flash("No file selected")
            return redirect(request.url)

        file = request.files["image"]
        password = request.form["password"]

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)

            # Convert to PNG
            img = Image.open(filepath).convert("RGB")
            png_name = os.path.splitext(filename)[0] + "_reveal.png"
            png_path = os.path.join(app.config["UPLOAD_FOLDER"], png_name)
            img.save(png_path, format="PNG")

            try:
                encrypted_message = decode_message(png_path)
                decrypted_message = decrypt_message(encrypted_message, password)
                return render_template("result.html", result="Hidden Message: " + decrypted_message)
            except Exception:
                flash("Wrong password or corrupted image!")
                return redirect(request.url)

    return render_template("reveal.html")


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


if __name__ == "__main__":
    app.run(debug=True)