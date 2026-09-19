from django.db import models
from django.utils import timezone

class TrainStatus(models.Model):
    STATUS_CHOICES = (
        ('ON_TIME', 'On Time'),
        ('DELAYED', 'Delayed'),
        ('CANCELLED', 'Cancelled'),
    )
    train = models.ForeignKey('trains.Train', on_delete=models.CASCADE, related_name='statuses')
    date = models.DateField(default=timezone.now)
    current_station = models.ForeignKey('stations.Station', on_delete=models.SET_NULL, null=True, related_name='current_status')
    next_station = models.ForeignKey('stations.Station', on_delete=models.SET_NULL, null=True, blank=True, related_name='next_status')
    delay_minutes = models.PositiveIntegerField(default=0)
    status_message = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ON_TIME')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('train', 'date')
        
    def __str__(self):
        return f"{self.train.number} on {self.date} - {self.status_message}"
