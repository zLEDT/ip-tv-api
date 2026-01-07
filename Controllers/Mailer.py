from email.message import EmailMessage
import ssl, smtplib
from datetime import datetime,timedelta
from Controllers.loop import loop
class Correo():
    def __init__(self,datos):
        self.receptores = []
        self.emisor = "alcafivideos@gmail.com"
        self.passemisor = "cfos nmgz tave tocm"     
        self.receptores =  ["alcafi.81@gmail.com","leondeltorito998@gmail.com"]

    @loop
    def send(self,asunto,cuerpo):
       try: 
        emisor = self.emisor
        receptor = self.receptores
        passemisor = self.passemisor
        

        subject = asunto
        now = datetime.now()
        hora = now.strftime("%H:%M")
        dia = now.strftime("%d/%m/%Y")

        #Enviando correo a todos los emails
        em = EmailMessage()
        em['From'] = emisor
        em['To'] = receptor
        em['Subject'] = subject
        
        em.set_content(f"""<!DOCTYPE html>
                            <html>
                            <head>
                                <link href="https://fonts.googleapis.com/css?family=Inter&display=swap" rel="stylesheet" />
                                <title>Document</title>
                            </head>
                            <body style="font-size: 14px;">
                                {cuerpo}
                            </body>
                        </html>
                       """,subtype='html')
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com',465,context=context) as smtp:
            smtp.login(emisor,passemisor)
            smtp.sendmail(emisor,receptor,em.as_string())
            
       except Exception as e:
            print(e)