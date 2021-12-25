from flask_mail import Message
import os, time

def crear_correo(remitente, destinatario, asunto, texto):
    mensaje = Message(asunto, sender=remitente, recipients=[destinatario])
    mensaje.body = texto
    return mensaje