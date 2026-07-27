from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class LostItemReport(models.Model):
    CATEGORY_CHOICES = [
        ("mobile", "Mobile Phone"),
        ("laptop", "Laptop"),
        ("tablet", "Tablet"),
        ("earbuds", "Earbuds / Headphones"),
        ("watch", "Watch / Smartwatch"),
        ("wallet", "Wallet / Purse"),
        ("bag", "Bag"),
        ("id_card", "ID Card / Certificate"),
        ("keys", "Keys"),
        ("jewellery", "Jewellery"),
        ("vehicle", "Vehicle"),
        ("document", "Document"),
        ("electronics", "Other Electronics"),
        ("other", "Other Item"),
    ]

    STATUS_CHOICES = [
        ("not_found", "Not Found"),
        ("found", "Found"),
        ("closed", "Closed"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    brand = models.CharField(max_length=255, blank=True, null=True)
    model = models.CharField(max_length=255, blank=True, null=True)
    color = models.CharField(max_length=100, blank=True, null=True)
    estimated_value = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField()

    imei_number = models.CharField(max_length=50, blank=True, null=True)
    serial_number = models.CharField(max_length=100, blank=True, null=True)
    vehicle_number = models.CharField(max_length=50, blank=True, null=True)

    item_image = models.ImageField(upload_to="lost_items/images/", blank=True, null=True)
    ownership_bill = models.FileField(upload_to="lost_items/bills/", blank=True, null=True)

    lost_date = models.DateField()
    lost_time = models.TimeField(blank=True, null=True)
    lost_place_text = models.CharField(max_length=255)
    latitude = models.CharField(max_length=50, blank=True, null=True)
    longitude = models.CharField(max_length=50, blank=True, null=True)

    contact_name = models.CharField(max_length=255)
    contact_phone = models.CharField(max_length=20)
    contact_email = models.EmailField()
    alternate_contact = models.CharField(max_length=100, blank=True, null=True)

    reward_note = models.CharField(max_length=255, blank=True, null=True)
    extra_notes = models.TextField(blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="not_found")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class FoundItemReport(models.Model):
    CATEGORY_CHOICES = LostItemReport.CATEGORY_CHOICES

    STATUS_CHOICES = [
        ("unclaimed", "Unclaimed"),
        ("matched", "Matched"),
        ("returned", "Returned"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    brand = models.CharField(max_length=255, blank=True, null=True)
    model = models.CharField(max_length=255, blank=True, null=True)
    color = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField()

    imei_number = models.CharField(max_length=50, blank=True, null=True)
    serial_number = models.CharField(max_length=100, blank=True, null=True)
    vehicle_number = models.CharField(max_length=50, blank=True, null=True)

    item_image = models.ImageField(upload_to="found_items/images/", blank=True, null=True)

    found_date = models.DateField()
    found_time = models.TimeField(blank=True, null=True)
    found_place_text = models.CharField(max_length=255)
    latitude = models.CharField(max_length=50, blank=True, null=True)
    longitude = models.CharField(max_length=50, blank=True, null=True)

    finder_name = models.CharField(max_length=255)
    finder_phone = models.CharField(max_length=20)
    finder_email = models.EmailField()
    extra_notes = models.TextField(blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="unclaimed")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class ItemMatch(models.Model):
    lost_item = models.ForeignKey(LostItemReport, on_delete=models.CASCADE)
    found_item = models.ForeignKey(FoundItemReport, on_delete=models.CASCADE)
    matched_at = models.DateTimeField(auto_now_add=True)
    contacts_visible_after = models.DateTimeField(blank=True, null=True)
    is_confirmed = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.contacts_visible_after:
            self.contacts_visible_after = timezone.now() + timedelta(days=1)
        super().save(*args, **kwargs)

    @property
    def contacts_are_visible(self):
        return timezone.now() >= self.contacts_visible_after

    def __str__(self):
        return f"{self.lost_item.title} ↔ {self.found_item.title}"


class ContactComplaint(models.Model):
    SUBJECT_CHOICES = [
        ("general_inquiry", "General Inquiry"),
        ("technical_issue", "Technical Issue"),
        ("account_support", "Account Support"),
        ("report_concern", "Report Concern"),
        ("feedback", "Feedback / Suggestion"),
        ("complaint", "Complaint"),
    ]

    STATUS_CHOICES = [
        ("new", "New"),
        ("in_progress", "In Progress"),
        ("resolved", "Resolved"),
        ("closed", "Closed"),
    ]

    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    subject = models.CharField(max_length=50, choices=SUBJECT_CHOICES)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.subject}"


class UserPreference(models.Model):
    LANGUAGE_CHOICES = [
        ("en", "English"),
        ("ta", "Tamil"),
        ("ml", "Malayalam"),
        ("ms", "Malay"),
        ("hi", "Hindi"),
        ("si", "Sinhala"),
    ]

    REGION_CHOICES = [
        ("India", "India"),
        ("Sri Lanka", "Sri Lanka"),
        ("Malaysia", "Malaysia"),
        ("Singapore", "Singapore"),
        ("Canada", "Canada"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="preferences")

    email_notifications = models.BooleanField(default=True)
    match_alerts = models.BooleanField(default=True)
    claim_updates = models.BooleanField(default=True)

    contact_after_match = models.BooleanField(default=True)
    hide_sensitive_details = models.BooleanField(default=True)
    activity_logging = models.BooleanField(default=True)

    otp_verification = models.BooleanField(default=True)
    google_login_access = models.BooleanField(default=True)
    login_alerts = models.BooleanField(default=True)

    save_search_history = models.BooleanField(default=True)
    save_report_drafts = models.BooleanField(default=True)
    personalized_suggestions = models.BooleanField(default=True)

    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default="en")
    region = models.CharField(max_length=20, choices=REGION_CHOICES, default="India")

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} preferences"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(upload_to="profile_pics/", blank=True, null=True)

    def __str__(self):
        return self.user.username