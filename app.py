import os

import asyncio
from sanic import Sanic
from sanic.response import html

from fetch_imgs import generate_image


app = Sanic(__name__)
app.static('/static', f'{os.path.dirname(__file__)}/static')


@app.route('/')
async def index(request):
    image_path = os.path.join(os.path.dirname(__file__), 'static/img.jpeg')

    if os.path.exists(image_path):
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>General Python Developer interview</title>
        </head>
        <body>
            <img src="/static/img.jpeg" alt="Image">
        </body>
        </html>
        """
        return html(html_content)
    else:
        return html("Image not found")


if __name__ == '__main__':
    img = asyncio.run(generate_image('static/img.jpeg'))
    app.run(host='0.0.0.0', port=8000)
