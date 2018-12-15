# Image-Classifer-with-Telegram-UI
python machine learning project with telegram ui

In order to use this project, you have to enable your own redis database.
Here is the hyper link to download redis: https://redis.io/download

There are three components in this system:

bot.py: a program that keep receiving user messages from Telegram, and is also responsible for sending response back to the user
image_downloader.py: a program that is responsible for downloading images from either Telegram or a given URL
predict.py: a program that loads a PyTorch pre-trained model for object recognition, and generates predictions when given an image
