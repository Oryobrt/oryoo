from rest_framework import serializers
from .models import License

class LicenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = License
        fields = ['license_key', 'hwid', 'expiry_date', 'activated_on']  # You can include other fields if needed
