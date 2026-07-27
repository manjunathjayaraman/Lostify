from django.contrib import admin
from .models import (
    LostItemReport,
    FoundItemReport,
    ItemMatch,
    ContactComplaint,
    UserPreference,
    Profile,
)


@admin.register(LostItemReport)
class LostItemReportAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'category',
        'contact_name',
        'contact_email',
        'status',
        'created_at',
    )
    search_fields = (
        'title',
        'category',
        'brand',
        'model',
        'contact_name',
        'contact_email',
        'imei_number',
        'serial_number',
        'vehicle_number',
    )
    list_filter = (
        'category',
        'status',
        'created_at',
    )


@admin.register(FoundItemReport)
class FoundItemReportAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'category',
        'finder_name',
        'finder_email',
        'status',
        'created_at',
    )
    search_fields = (
        'title',
        'category',
        'brand',
        'model',
        'finder_name',
        'finder_email',
        'imei_number',
        'serial_number',
        'vehicle_number',
    )
    list_filter = (
        'category',
        'status',
        'created_at',
    )


@admin.register(ItemMatch)
class ItemMatchAdmin(admin.ModelAdmin):
    list_display = (
        'lost_item',
        'found_item',
        'is_confirmed',
        'matched_at',
        'contacts_visible_after',
    )
    search_fields = (
        'lost_item__title',
        'found_item__title',
    )
    list_filter = (
        'is_confirmed',
        'matched_at',
    )


@admin.register(ContactComplaint)
class ContactComplaintAdmin(admin.ModelAdmin):
    list_display = (
        'full_name',
        'email',
        'subject',
        'status',
        'created_at',
    )
    search_fields = (
        'full_name',
        'email',
        'phone_number',
        'message',
    )
    list_filter = (
        'subject',
        'status',
        'created_at',
    )


@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'language',
        'region',
        'updated_at',
    )
    search_fields = (
        'user__username',
        'user__email',
    )
    list_filter = (
        'language',
        'region',
        'updated_at',
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'phone_number',
        'location',
    )
    search_fields = (
        'user__username',
        'user__email',
        'phone_number',
        'location',
    )