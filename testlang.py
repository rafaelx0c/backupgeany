import smtplib

EMAIL_ADDRESS = "raspiberry019@gmail.com"
EMAIL_PASSWORD = "ljud ljwu kcof aele"

try:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    server.sendmail(EMAIL_ADDRESS, "recipient_email@gmail.com", "Test email")
    server.quit()
    print("Email sent successfully!")
except Exception as e:
    print(f"Error: {e}")
