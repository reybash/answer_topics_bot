import email.mime.application
import os
from email.mime.multipart import MIMEMultipart

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message
from aiosmtplib import SMTP

from bot.consts import EMAIL, SUBJECT, ADMINS_EMAILS, ADMINS_IDS
from bot.file_handlers import read_addressee


async def send_mail(to, file_bytes, filename):
    message = MIMEMultipart()
    message["From"] = EMAIL
    message["To"] = to
    message["Subject"] = SUBJECT
    att = email.mime.application.MIMEApplication(file_bytes, _subtype="docx")
    att.add_header('Content-Disposition', 'attachment', filename=filename)
    message.attach(att)

    smtp_client = SMTP(hostname="smtp.yandex.ru", port=465, use_tls=True)
    async with smtp_client:
        await smtp_client.login(EMAIL, os.environ.get("EMAIL_PWD"))
        await smtp_client.send_message(message)


async def send_document_to_email(file_bytes, filename):
    try:
        for mail in read_addressee(ADMINS_EMAILS):
            await send_mail(mail, file_bytes, filename)
    except FileNotFoundError:
        await send_mail(EMAIL, file_bytes, filename)


async def send_document_to_tg(message: Message, output_file):
    try:
        for admin_id in read_addressee(ADMINS_IDS):
            try:
                await message.bot.send_document(int(admin_id), output_file)
            except TelegramBadRequest:
                pass
    except FileNotFoundError:
        await message.answer_document(output_file)
