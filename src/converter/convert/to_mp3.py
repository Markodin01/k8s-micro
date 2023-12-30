import pika
import json
import tempfile
import os
from bson.objectid import ObjectId
import moviepy.editor as mp

def start(message, fs_videos, fs_mp3s, channel):
    message = json.loads(message)

    # Use a single with statement for file operations
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        out = fs_videos.get(ObjectId(message["video_fid"])).read()
        tf.write(out)

    # Use moviepy to extract audio
    tf_path = tempfile.gettempdir() + f"/{message['video_fid']}.mp3"
    audio = mp.VideoFileClip(tf.name).audio
    audio.write_audiofile(tf_path)

    # Read the audio file and upload it to fs_mp3s
    with open(tf_path, "rb") as f:
        data = f.read()
        fid = fs_mp3s.put(data)
        os.remove(tf_path)

    message["mp3_fid"] = str(fid)

    try:
        channel.basic_publish(
            exchange='',
            routing_key=os.environ.get("MP3_QUEUE"),
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE,  # or use 2 directly
            )
        )
    except Exception as err:
        fs_mp3s.delete(fid)
        print(f"Failed to publish message to mp3 queue. Error: {err}")
        return "failed to publish message to mp3 queue"
