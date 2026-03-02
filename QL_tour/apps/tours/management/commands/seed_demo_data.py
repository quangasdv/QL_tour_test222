from django.utils import timezone
from django.core.management import BaseCommand
from django.contrib.gis.geos import Point

from ....tours.models import Tour, Category


class Command(BaseCommand):
    help = "Seed demo data for Tour"

    def handle(self, *args, **options):
        cat_adv, _ = Category.objects.get_or_create(
            name="Du lịch Mạo hiểm"
        )

        Tour.objects.get_or_create(
            title="Chinh phục Hang Sơn Đoòng",
            description="Thám hiểm hang động lớn nhất thế giới.",
            price=2500000,
            duration_days= timezone.now(),
            max_people= 5,
            category= cat_adv,
        )

        self.stdout.write(self.style.SUCCESS("Demo data created successfully"))