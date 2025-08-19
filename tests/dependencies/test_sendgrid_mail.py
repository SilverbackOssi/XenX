import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import dotenv
dotenv.load_dotenv()

message = Mail(
    from_email='anyimossi.dev@gmail.com',
    to_emails='ossifavour@gmail.com',
    subject='Sending with Twilio SendGrid is Fun',
    html_content='<strong>and easy to do anywhere, even with Python</strong>')
try:
    sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY', '7890'))
    # sg.set_sendgrid_data_residency("eu")
    # uncomment the above line if you are sending mail using a regional EU subuser
    response = sg.send(message)
    print(response.status_code)
    print(response.body)
    print(response.headers)
except Exception as e:
    print(e.message)