from django.db import models

class RapidAPIHistory(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    train_number = models.CharField(max_length=50, null=True, blank=True)
    request_params = models.JSONField(null=True, blank=True)
    endpoint = models.CharField(max_length=255)
    http_status = models.IntegerField()
    success = models.BooleanField()
    response_json = models.JSONField()

    class Meta:
        db_table = 'rapid_api_history'
