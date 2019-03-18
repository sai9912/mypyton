import csv

from django.contrib import messages
from django.contrib.admin import ModelAdmin
from django.http import HttpResponse

from products.tasks import update_gs1_cloud_product


def gs1_cloud_draft_action(description, state='DRAFT'):
    """
    GO/MO admins are able to reset ACTIVE status to DRAFT
    """

    def draft_action(modeladmin, request, queryset):
        queryset.update(gs1_cloud_state=state)
        for product in queryset.all():
            update_gs1_cloud_product.delay(product, None, request.user, force=True)

        count = queryset.all().count()
        messages.add_message(
            request,
            messages.INFO,
            f'{count} products are marked as "DRAFT", GS1 cloud upload is pending.'
        )

    # if you want to use this method multiple times with different parameters
    # it seems it's required to generate a random function name which will be returned later
    draft_action.short_description = description
    return draft_action


def gs1_cloud_reactivate_action(description, state='ACTIVE'):
    """
    GO/MO admins are able to reactivate products again even if they already has active status
    """

    def activate_action(modeladmin, request, queryset):
        queryset.update(gs1_cloud_state=state)
        for product in queryset.all():
            update_gs1_cloud_product.delay(product, None, request.user, force=True)

        count = queryset.all().count()
        messages.add_message(
            request,
            messages.INFO,
            f'{count} products are marked as "ACTIVE", GS1 cloud upload is pending.'
        )

    # if you want to use this method multiple times with different parameters
    # it seems it's required to generate a random function name which will be returned later
    activate_action.short_description = description
    return activate_action

