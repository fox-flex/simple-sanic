import os
from pathlib import Path

import numpy as np
import cv2
from PIL import Image

from io import BytesIO
import aiohttp
import asyncio

async def fetch_url(url: str, num_imgs: int = 132):
    params = {'limit': num_imgs, 'offset': 0}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            assert resp.status == 200
            imgs = await resp.json()
            imgs = imgs['photos']
            assert len(imgs) == 132
    return imgs


def stack_imgs(imgs: list[np.array], size: tuple) -> np.array:
    # size: (h, w)
    assert len(size) == 2 and size[0]*size[1] == len(imgs)
    h, w = size

    rows = [np.hstack(imgs[i*w: (i+1)*w]) for i in range(h)]
    img = np.vstack(rows)
    return img

async def generate_image(img_path: str):
    url = 'https://api.slingacademy.com/v1/sample-data/photos'
    imgs_data = await fetch_url(url)
    imgs = [None] * len(imgs_data)

    async def load_image(i: int, size=(32, 32)):
        img_url = imgs_data[i]['url']
        async with aiohttp.ClientSession() as session:
            async with session.get(img_url) as resp:
                if resp.status == 200:
                    img = await resp.read()
                    try:
                        img = Image.open(BytesIO(img))
                        img = np.asarray(img)
                        img = cv2.resize(img, size, interpolation=cv2.INTER_LINEAR)
                        print(f'success fetch {img_url}')
                    except Exception as _:
                        img = np.zeros((*size, 3), np.uint8)
                        img[..., 2] = 255  # RGB image
                        print(f'failed to convert image {img_url}')
                else:
                    print(f'fail fetch {img_url}')
                    # generate black image
                    img = np.zeros((*size, 3), np.uint8)
                    return
        imgs[i] = img
    await asyncio.gather(*[load_image(i) for i, _ in enumerate(imgs_data)])

    img = stack_imgs(imgs, size=(11, 12))
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    Path(os.path.dirname(img_path)).mkdir(parents=True, exist_ok=True)
    cv2.imwrite(img_path, img)
