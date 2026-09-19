from django.db import models

class Schedule(models.Model):
    train = models.ForeignKey('trains.Train', on_delete=models.CASCADE, related_name='schedules')
    station = models.ForeignKey('stations.Station', on_delete=models.CASCADE)
    arrival_time = models.TimeField(null=True, blank=True)
    departure_time = models.TimeField(null=True, blank=True)
    day_count = models.PositiveIntegerField(default=1)
    
    class Meta:
        ordering = ['day_count', 'arrival_time']
        unique_together = ('train', 'station')

    def __str__(self):
        return f"{self.train.number} at {self.station.code}"
