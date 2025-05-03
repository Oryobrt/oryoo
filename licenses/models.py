from django.db import models
from django.utils import timezone

class License(models.Model):
    license_key = models.CharField(max_length=50, unique=True)
    hwid = models.CharField(max_length=50, blank=True, null=True)  # Allow hwid to be null
    expiry_date = models.DateTimeField()
    activated_on = models.DateTimeField()
    email = models.EmailField(blank=True, null=True)  # Add the email field here
    last_hwid_reset = models.DateTimeField(null=True, blank=True)  # Changed to DateTimeField
    meta = models.JSONField(default=dict)  # Assuming you use JSON for extra data

    def __str__(self):
        return self.license_key

    def is_valid(self):
        if not self.expiry_date:
            return False
        return self.expiry_date > timezone.now()

    def is_hwid_matched(self, hwid):
        return self.hwid == hwid

    def bind_hwid(self, hwid):
      if self.hwid != hwid:  # Only bind if it's different
        self.hwid = hwid
        self.last_hwid_reset = timezone.now()
        self.save()  # ← this is what persists the change

