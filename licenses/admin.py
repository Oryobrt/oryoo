from django.contrib import admin
from .models import License

class LicenseAdmin(admin.ModelAdmin):
    list_display = ('license_key', 'hwid', 'expiry_date', 'activated_on', 'is_valid')  # Display these fields in the list view
    search_fields = ('license_key', 'hwid')  # Allow searching by license_key and hwid
    list_filter = ('expiry_date', 'activated_on')  # Filter licenses by expiry date and activation date

    def is_valid(self, obj):
        return obj.is_valid()
    is_valid.boolean = True
    is_valid.short_description = 'Valid'

admin.site.register(License, LicenseAdmin)
    