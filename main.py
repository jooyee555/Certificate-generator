from flask import Flask, render_template, request, send_file
from PIL import Image, ImageDraw, ImageFont
import io
import os

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")


def draw_text_multiline_center(draw, text, font, img_width, y_center, max_width, fill):
    words = text.split()
    line = ""


    bbox = font.getbbox("A")  
    line_height = (bbox[3] - bbox[1]) * 1.2

    
    lines = []
    for word in words:
        test_line = line + word + " "

        line_width = font.getlength(test_line)
        if line_width > max_width and line:
            lines.append(line)
            line = word + " "
        else:
            line = test_line
    lines.append(line)


    total_height = len(lines) * line_height
    start_y = y_center - total_height / 2  
    for idx, line_text in enumerate(lines):
        line_width = font.getlength(line_text)
        x = (img_width - line_width) / 2  
        draw.text((x, start_y + idx * line_height), line_text, font=font, fill=fill)

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


    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()


    max_width_px = img.width * (max_width_pct / 100)


    if v_pos_pct == 10:
        v_pos_px = img.height / 2
    else:
        v_pos_px = img.height * (v_pos_pct / 100)


    draw_text_multiline_center(draw, text, font, img.width, v_pos_px, max_width_px, color)


    pdf_bytes = io.BytesIO()
    img.save(pdf_bytes, "PDF", resolution=100.0)
    pdf_bytes.seek(0)

    return send_file(
        pdf_bytes,
        as_attachment=True,
        download_name=pdf_filename,
        mimetype="application/pdf"
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
