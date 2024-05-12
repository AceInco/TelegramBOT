import logging
import os
from time import strftime

import filetype
import requests
import yt_dlp
from yt_dlp import YoutubeDL
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from credentials import bot_token

TOKEN = bot_token


# logging.basicConfig(
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     level=logging.INFO
# )


ydl_opts = {
    "quiet": True,
    "format": "best",
    "outtmpl": f"videos/{strftime('%Y_%m_%d_%H_%M_%S')}%(title)s.%(ext)s",
    'postprocessors': [{
        'key': 'FFmpegVideoConvertor',
        'preferedformat': 'mp4',
    }],
    # 'ffmpeg_location': "C:/Users/Kirill/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget"
    #                    ".Source_8wekyb3d8bbwe/ffmpeg-7.0-full_build/bin",
    "keepfile": True

}


def check_for_url(url):
    try:
        return requests.get(url)
    except requests.RequestException:
        return None


def check_for_image(response):
    if 'image' in response.headers['Content-Type']:
        image_type = filetype.image_match(response.content)
        if image_type:
            return True
    return False


def check_for_video(video_url):
    try:
        with YoutubeDL() as ydl:
            ydl.extract_info(video_url, download=False)
            return True
    except yt_dlp.DownloadError:
        return False


async def send_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = " ".join(context.args)

    response = check_for_url(url)

    if response:
        if check_for_image(response):
            extension = os.path.basename(response.headers['Content-Type'])
            filename = 'image_{0}{1}'.format(strftime("%Y_%m_%d_%H_%M_%S"), '.' + str(extension))
            with open(f"images/{filename}", 'wb+') as image:
                image.write(response.content)
            await context.bot.send_photo(chat_id=update.effective_chat.id, photo=f"images/{filename}")
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="URL is not an image")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Not valid URL")


async def send_video(update: Update, context: ContextTypes.DEFAULT_TYPE):

    url = " ".join(context.args)

    response = check_for_url(url)

    if response:
        if check_for_video(url):
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)

            await context.bot.send_video(chat_id=update.effective_chat.id, video=filename.replace("\\", "/"))
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="URL is not a video")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Not valid URL")


if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()

    img_handler = CommandHandler("image", send_image)
    video_handler = CommandHandler("video", send_video)

    application.add_handler(img_handler)
    application.add_handler(video_handler)

    application.run_polling()
