from django.core.management.base import BaseCommand
from django.utils import timezone
from licenses.models import License
from datetime import timedelta


class Command(BaseCommand):
    help = "Inspects and fixes missing or broken fields in License records."

    def handle(self, *args, **options):
        now = timezone.now()
        licenses = License.objects.all()
        updated_count = 0

        self.stdout.write("Inspecting license records...\n")

        for lic in licenses:
            changed = False
            self.stdout.write(f"--- {lic.license_key} ---")
            self.stdout.write(f"HWID         : {lic.hwid}")
            self.stdout.write(f"Activated on : {lic.activated_on}")
            self.stdout.write(f"Expires on   : {lic.expiry_date}")

            # Fix missing activated_on
            if not lic.activated_on:
                lic.activated_on = now
                self.stdout.write(self.style.WARNING(" -> Fixed: 'activated_on' was missing. Set to now."))
                changed = True

            # Fix expiry_date (missing or expired)
            if not lic.expiry_date or lic.expiry_date <= now:
                lic.expiry_date = now + timedelta(days=30)
                self.stdout.write(self.style.WARNING(" -> Fixed: 'expiry_date' was missing or expired. Set to +30 days."))
                changed = True

            # Warn if HWID is missing
            if not lic.hwid:
                self.stdout.write(self.style.NOTICE(" -> Warning: HWID is not set."))
                # Optional fix:
                # lic.hwid = "TEST-HWID-PLACEHOLDER"
                # changed = True

            if changed:
                lic.save()
                updated_count += 1
                self.stdout.write(self.style.SUCCESS(" -> Saved updated license.\n"))
            else:
                self.stdout.write(" -> No changes needed.\n")

        self.stdout.write(self.style.SUCCESS(f"Finished. {updated_count} license(s) were updated."))
