from rest_framework import serializers

allowed_url = ["youtube.com", "www.youtube.com"]


class UrlValidator:
    def __init__(self, field):
        self.field = field

    def __call__(self, data):
        value = data.get(self.field)

        if not value:
            return

        if not value.startswith(
            (
                "http://",
                "https://",
            )
        ):
            raise serializers.ValidationError("Некорректный URL")

        value_host = value.split("/")[2].strip().lower()

        if value_host not in allowed_url:
            raise serializers.ValidationError(f"Запрещенный URL, разрешены только эти хосты: {', '.join(allowed_url)}")

        return
