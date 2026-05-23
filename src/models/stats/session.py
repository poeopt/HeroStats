from datetime import datetime


class Session:
    start_time: datetime
    has_mail: bool = False

    def __init__(self):
        self.start_time = datetime.now()
        self.has_mail = False

    def update(self, has_mail=None):
        if has_mail is not None:
            self.has_mail = has_mail

    def get_duration(self):
        return datetime.now() - self.start_time

    def get_duration_str(self):
        return str(self.get_duration()).split(".")[0]

    def calculate_value_per_hour(self, value: int) -> int:
        total_sec = self.get_duration().total_seconds()  # BUG FIX: was .seconds
        if total_sec < 1:
            return 0
        return int(value / (total_sec / 3600))
