from django.db import models
from django.utils import timezone


class Log(models.Model):
    logger = models.CharField(max_length=50, null=True)  # the name of the logger. (e.g. myapp.views)
    level = models.CharField(max_length=10, null=True)  # info, debug, or error?
    trace = models.TextField(null=True)  # the full traceback printout
    msg = models.TextField(null=True)  # any custom log you may have included
    ip_address = models.CharField(max_length=15, null=True)  # ip address
    username = models.CharField(max_length=50, null=True)
    created_at = models.DateTimeField(default=timezone.now)  # the current timestamp


class ServiceManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()

    def log(self, user, key, gs1_cloud_last_rc, msg, ref):
        cloud_log = CloudLog(username=user.email,
                             key=key,
                             gs1_cloud_last_rc=gs1_cloud_last_rc,
                             msg=msg,
                             ref=ref)
        cloud_log.save()


class CloudLog(models.Model):
    username = models.CharField(max_length=50, null=True)
    msg = models.TextField(null=True)                 # any custom log you may have included
    ref = models.CharField(max_length=50, null=True)  # sync reference
    key = models.CharField(max_length=50, null=True)  # GS1 KEY ( GTIN/GLN )
    gs1_cloud_last_rc = models.CharField(max_length=50, null=True)
    created_at = models.DateTimeField(default=timezone.now)  # the current timestamp

    objects = models.Manager()
    service = ServiceManager()


cloud_log_service = CloudLog.service
