from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import License
from .serializers import LicenseSerializer

@api_view(['GET'])
def verify_license(request):
    license_key = request.GET.get('license_key')
    if not license_key:
        return Response({'error': 'License key is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        license = License.objects.get(license_key=license_key)
        serializer = LicenseSerializer(license)
        return Response(serializer.data)
    except License.DoesNotExist:
        return Response({'error': 'Invalid license key'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def bind_hwid(request):
    license_key = request.data.get('license_key')
    hwid = request.data.get('hwid')

    if not license_key or not hwid:
        return Response({'error': 'license_key and hwid are required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        license = License.objects.get(license_key=license_key)
        if license.hwid:
            return Response({'error': 'HWID already set for this license.'}, status=status.HTTP_400_BAD_REQUEST)
        
        license.hwid = hwid
        license.save()
        return Response({'message': 'HWID bound successfully.'})
    except License.DoesNotExist:
        return Response({'error': 'License not found.'}, status=status.HTTP_404_NOT_FOUND)
