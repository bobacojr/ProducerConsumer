from django.db import models

# TaskOutput data taken from the producer and consumer celery workers
class TaskOutput(models.Model):
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

# SharedBuffer data used by producer and consumer celery workers
class SharedBuffer(models.Model):
    buffer = models.JSONField(default=list)
    bufferSize = models.IntegerField(default=10)
    in_index = models.IntegerField(default=0)
    out_index = models.IntegerField(default=0)
    count = models.IntegerField(default=0)
    producerSleepTime = models.FloatField(default=1.0)
    consumerSleepTime = models.FloatField(default=1.5)
    shouldTerminate = models.BooleanField(default=False)
    producerFinished = models.BooleanField(default=False)