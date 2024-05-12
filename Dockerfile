FROM python:3.10

WORKDIR /app

COPY . /app

# Install FFmpeg
RUN apt-get update && apt-get install -y ffmpeg

# Install yt-dlp
RUN pip install --no-cache-dir -r requirements.txt

# Run your script
CMD ["python", "app.py"]