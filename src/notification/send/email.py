import stmplib, os
from email.message import EmailMessage

def notification(message):
    try:
        message = json.loads(message)
        mp3_fid = message["mp3_fid"]
        sender_address = os.environ.get("SENDER_ADDRESS")
        sender_password = os.environ.get("SENDER_PASSWORD")
        receiver_address = message['username']

        msg = EmailMessage()
        msg.set_content(f"mp3 file_id: {mp3_fid} is now ready")
        msg['Subject'] = 'Your mp3 file is ready'
        msg['From'] = sender_address
        msg['To'] = receiver_address

        session = smtplib.SMTP('smtp.gmail.com')
        session.starttls()
        session.login(sender_address, sender_password)
        session.send_message(msg, sender_address, receiver_address)
        session.quit()

    except Exception as e:
        print(f"Error sending email: {e}")
        return e