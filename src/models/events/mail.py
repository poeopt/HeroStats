from src.models.messages.mail import MailMessage
from src.models.events.base import BaseEvent
from src.consts import events as consts


class MailEvent(BaseEvent):
    value: int

    def __init__(self, mail_message: MailMessage):
        self.name = consts.EvNameUpdateMail  # BUG FIX: was EvNameUpdateXP
        self.value = mail_message.new_mail
