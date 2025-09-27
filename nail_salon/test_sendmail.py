import smtplib

EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USER = "dohieu825@gmail.com"
EMAIL_PASS = "ntrr epwn umzd ewej"

try:
    server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
    server.starttls()
    server.login(EMAIL_USER, EMAIL_PASS)
    print("Login successful!")
    server.quit()
except Exception as e:
    print("Error:", e)
