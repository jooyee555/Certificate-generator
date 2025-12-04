from flask import Flask, render_template, request, send_file
from PIL import Image, ImageDraw, ImageFont
import io
import os

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")


def draw_text_multiline_center(draw, text, font, img_width, y, max_width_px, fill):
    words = text.split(' ')
    line = ''
    lines = []

    font_size = font.size
    line_height = font_size * 1.2

    for word in words:
        test_line = line + word + ' '
        if draw.textlength(test_line, font=font) > max_width_px and line:
            lines.append(line)
            line = word + ' '
        else:
            line = test_line

    lines.append(line)

    # Match canvas: top baseline (NOT centered)
    start_y = y

    for i, line_text in enumerate(lines):
        line_width = draw.textlength(line_text, font=font)
        x = (img_width - line_width) / 2
        draw.text((x, start_y + i * line_height), line_text, font=font, fill=fill)

@app.route("/generate", methods=["POST"])
def generate():
    img_file = request.files["image"]
    img = Image.open(img_file.stream).convert("RGB")

    text = request.form.get("text", "")
    font_size = int(request.form.get("font_size", 40))
    max_width_pct = int(request.form.get("max_width", 90))
    v_pos_pct = int(request.form.get("v_position", 10))
    color = request.form.get("text_color", "#FFFFFF")

    pdf_filename = request.form.get("pdf_filename", "output")
    if not pdf_filename.lower().endswith(".pdf"):
        pdf_filename += ".pdf"

    draw = ImageDraw.Draw(img)

    font_path = os.path.join("static", "fonts", "OpenSans-Regular.ttf")
    font = ImageFont.truetype(font_path, font_size)

    # Convert percentages to pixels (same as canvas)
    max_width_px = img.width * (max_width_pct / 100)
    y = img.height * (v_pos_pct / 100)

    draw_text_multiline_center(draw, text, font, img.width, y, max_width_px, color)

    pdf_bytes = io.BytesIO()
    img.save(pdf_bytes, "PDF", resolution=100.0)
    pdf_bytes.seek(0)

    return send_file(pdf_bytes,
                     as_attachment=True,
                     download_name=pdf_filename,
                     mimetype="application/pdf")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
