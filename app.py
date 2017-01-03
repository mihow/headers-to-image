from __future__ import print_function

from flask import Flask, request, jsonify, send_file, redirect, url_for
from PIL import Image, ImageDraw
import StringIO


app = Flask(__name__)


def request_headers_str():
    headers = [u"{}: {}".format(k, v) for k,v in request.headers.items()]
    headers_str = u"\n\r".join(headers)
    return headers_str

def create_image(txt):
    image = Image.new("RGBA", (600,150), (255,255,255))
    draw = ImageDraw.Draw(image)

    draw.text((10, 0), txt, (0,0,0))
    return image

def serve_image(pil_img):
    img_io = StringIO.StringIO()
    pil_img.save(img_io, 'JPEG', quality=70)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')

@app.route('/image.jpg')
def image():
    headers = request_headers_str()
    img = create_image(headers) 
    return serve_image(img)

@app.route('/')
def index():
    return redirect(url_for('image'))
