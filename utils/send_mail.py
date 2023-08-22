import yagmail
from widgets.notify import Notify
import asynckivy

async def send_email(recipient, otp):
    try:
        sender_email = "Pynewhorizon@gmail.com"
        receiver_email = recipient
        password1 = "PyNeWhOrIzOn1"
        sender_password = "mkndzcslpskrqacd"
        yag = yagmail.SMTP(sender_email, sender_password)

        subject = "OTP Verification..."
        body = f"Your  One time password for the Money Watch App is {otp}"
        await asynckivy.run_in_thread(lambda: yag.send(receiver_email, subject, body))

    except Exception as e:
        print(f"Send Email Error{e}")
        Notify().notify(f"No internet connection", error=True)
