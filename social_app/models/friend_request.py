from django.db import models
from .user import User
from ..constants import PENDING, ACCEPTED, REJECTED


class FriendRequest(models.Model):
    from_user = models.ForeignKey(
        User, related_name="sent_requests", on_delete=models.CASCADE
    )
    to_user = models.ForeignKey(
        User, related_name="received_requests", on_delete=models.CASCADE
    )
    status = models.CharField(
        max_length=20,
        choices=[
            (PENDING, PENDING),
            (ACCEPTED, ACCEPTED),
            (REJECTED, REJECTED),
        ],
    )

    def __str__(self):
        return f"{self.from_user} -> {self.to_user} : {self.status}"
