import pika, json

def upload(f, fs, channel, access):
    try:
        fid = fs.put(f)
    except Exception as e:
        return str(e), 500

    message = {
        "video_fid": str(fid),
        "mp3_fid": None,
        "username": access["username"]
    }

    try:
        channel.basic_publish(
            exchange="gateway",
            routing_key="convert",
            body=json.dumps(message),
            properties=pika.BasicProperties(
                pika.spec.PERSISTENT_DELIVERY_MODE)
        )

    except Exception as e:
        fs.delete(fid)
        return "failed to upload", 500

