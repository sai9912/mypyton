# Register your models here.

from django.contrib import admin

from .models import Log, CloudLog


@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'ip_address',
        'created_at',
    )
    search_fields = (
        'username',
    )


@admin.register(CloudLog)
class LogAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'msg',
        'ref',
        'key',
        'gs1_cloud_last_rc',
        'created_at',
    )

    search_fields = (
        'username',
        'key',
    )

