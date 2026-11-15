import os 
import resend

resend.api_key = os.getenv("RESEND_API_KEY")

def send_email(to, subject, html):
    try:
        params = {
            "from": os.getenv("MAIL_FROM"),
            "to":[to],
            "subject":subject,
            "html":html
        }

        response = resend.Emails.send(params)


        return True

    except Exception as e:
        print("Email sending failed: ",e)

        return False