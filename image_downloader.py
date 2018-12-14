#!/usr/bin/python
# -*- coding: UTF-8 -*-
import socket
import queue
import threading
import time
from PIL import Image
import requests
from io import BytesIO
import base64
import json
import struct

import redis
from redis import StrictRedis

r = StrictRedis(host='localhost', port=6379)
ENCODING = 'utf-8'
data = {}

def encodeImg(content):
    encoded_image = base64.b64encode(content)
    return encoded_image

while True:
    download = json.loads(r.blpop('download')[1].decode("utf-8"))
    print(download)
    response = requests.get(download["url"])
    send_image = response.content
    encoded_image = encodeImg(send_image)

    base64_string = encoded_image.decode(ENCODING)

    data["img"] = base64_string
    data["chat_id"] = download["chat_id"]
    message = json.dumps(data, indent=2)

    r.rpush('image', message.encode("utf-8"))