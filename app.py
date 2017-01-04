# -*- coding: utf-8 -*-
from __future__ import print_function

import StringIO

from flask import Flask, request, send_file, redirect, url_for, jsonify, render_template_string
from flask.json import JSONEncoder
from PIL import Image, ImageDraw
from nocache import nocache


app = Flask(__name__)
application = app


def mask_sensitive_data(data):
    sensi_keys = ['KEY', 'PASS', '_ID', '-ID',]
    if hasattr(data, 'items'):
        for k,v, in data.items():
            if hasattr(v, 'items'):
                v = mask_sensitive_data(v)
            else:
                for sk in sensi_keys:
                    if sk in k.upper():
                        data[k] = "*******"
    return data
             
def request_data():
    data = {} 
    data['headers'] = dict(request.headers) # HTTP headers
    data['query_args'] = dict(request.args)  # GET & POST vars
    data['environ'] = dict(request.environ)
    data['sensitive_test'] = {'TEST_API_KEY': 1234567878999,
                              'TEST_PASSWORD': 'happybirthday'}
    data = mask_sensitive_data(data)
    return data

def request_data_str():
    data = request_data()
    tmpl = """
    {% for k,v in data.items() %}{% if v.items %}{{ k }}: 
    {% for kk, vv in v.items() %}
    {{ kk }}: {{ vv }}{% endfor %} {% else %} 
    {{ k }}: {{ v }} {% endif %}

    {% endfor %}
    """
    txt =  render_template_string(tmpl, data=data)
    txt = txt.encode('utf8')
    return txt

def create_image(txt):
    image = Image.new("RGBA", (1024,1024), (255,255,255))
    draw = ImageDraw.Draw(image)

    draw.text((10, 0), txt, (0,0,0))
    return image

def serve_image(pil_img):
    img_io = StringIO.StringIO()
    pil_img.save(img_io, 'PNG', quality=90)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')

@app.route('/request_data.png')
@nocache
def as_image():
    txt = request_data_str()
    img = create_image(txt) 
    return serve_image(img)

@app.route('/request_data.html')
def as_html():
    data = request_data()
    tmpl = """
    <!doctype html>
    <html><body style="font-family: monospace;">
    <ul>
    {% for k,v in data.items() %}
    {% if v.items %}
    <li>{{ k }}: 
    <ul>{% for kk, vv in v.items() %}
    <li><b>{{ kk }}:</b> {{ vv }}</li>
    {% endfor %}
    </ul>
    {% else %}
    <li>{{ k }}: {{ v }}</li>
    {% endif %} 
    {% endfor %}
    </ul>
    </body></html>
    """
    return render_template_string(tmpl, data=data)


class CustomJSONEncoder(JSONEncoder):
    def default(self, o):
        return str(o)

app.json_encoder = CustomJSONEncoder
@app.route('/request_data.json')
def as_json():
    data = request_data()
    return jsonify(data), 200

@app.route('/')
def index():
    return redirect(url_for('embed'))

@app.route('/embed')
def embed():
    tmpl = """
    <!doctype html>
    <html><body>
    <h2>Select the image below and paste in your email body:</h2>
    <p>text before image</p>
    <p>
    <img src="{{ url_for('as_image', _external=True) }}" 
      title="Request data as image"
      alt="This should be an image with HTTP headers, etc">
    </p>
    <p>text after image</p>
    <p>&nbsp;</p>
    <h2>Or here is html for the image tag you can use:</h2>
    <p>
    <input 
      type="text" 
      value='<img src="{{ url_for('as_image', _external=True) }}">' 
      style="width:90%" />
    </p>
    <h2>Links</h2>
    <ul>
      <li><a href="{{ url_for('as_html') }}">
        Show request data as HTML</a></li>
      <li><a href="{{ url_for('as_json') }}">
        Show request data as JSON</a></li>
    </ul>
    </body></html>
    """
    return render_template_string(tmpl)
