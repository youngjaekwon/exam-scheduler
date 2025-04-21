from django.db import models


class ExamSchedule(models.Model):
    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    confirmed_participants = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["start_time"]
        indexes = [
            models.Index(fields=["start_time", "end_time"]),
        ]
