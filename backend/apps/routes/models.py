from django.db import models

class Route(models.Model):
    train = models.OneToOneField('trains.Train', on_delete=models.CASCADE, related_name='route')
    name = models.CharField(max_length=100, blank=True)

    def save(self, *args, **kwargs):
        if not self.name and hasattr(self, 'train'):
            self.name = f"{self.train.source.code} to {self.train.destination.code}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name or f"Route for {self.train_id}"

class RouteStation(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='stations')
    station = models.ForeignKey('stations.Station', on_delete=models.CASCADE)
    sequence_number = models.PositiveIntegerField()
    distance_from_source = models.PositiveIntegerField(help_text="Distance in km")
    arrival_time = models.TimeField(null=True, blank=True)
    departure_time = models.TimeField(null=True, blank=True)
    journey_day = models.PositiveIntegerField(default=1)
    
    class Meta:
        ordering = ['sequence_number']
        unique_together = ('route', 'station')
        
    def __str__(self):
        return f"{self.route.train.number} - {self.station.code} ({self.sequence_number})"
