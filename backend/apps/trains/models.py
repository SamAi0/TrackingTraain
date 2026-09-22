from django.db import models

class Train(models.Model):
    TRAIN_TYPES = (
        ('EXPRESS', 'Express'),
        ('LOCAL', 'Local'),
        ('PASSENGER', 'Passenger'),
        ('SUPERFAST', 'Superfast'),
        ('SLOW', 'Slow'),
        ('FAST', 'Fast'),
    )
    number = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=100)
    train_type = models.CharField(max_length=20, choices=TRAIN_TYPES, default='EXPRESS')
    source = models.ForeignKey('stations.Station', on_delete=models.CASCADE, related_name='source_trains')
    destination = models.ForeignKey('stations.Station', on_delete=models.CASCADE, related_name='destination_trains')
    running_days = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.number} - {self.name}"

    @property
    def normalized_type(self):
        local_types = ['Pass', 'DEMU', 'MEMU', 'LOCAL', 'Klkt', 'Hyd']
        if self.train_type in local_types:
            return 'LOCAL'
        return 'EXPRESS'
