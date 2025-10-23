from django.core.management.base import BaseCommand
from django.core.files import File
from django.conf import settings
from gallery.models import Lapangan
import os

class Command(BaseCommand):
    help = "Load lapangan from media/seed/ (one lapangan per image)"

    def handle(self, *args, **options):
        seed_dir = os.path.join(settings.MEDIA_ROOT, 'seed')
        if not os.path.exists(seed_dir):
            self.stdout.write(self.style.ERROR(f"Seed dir not found: {seed_dir}"))
            return

        files = sorted([f for f in os.listdir(seed_dir) if f.lower().endswith(('.jpg','.jpeg','.png'))])
        for idx, fname in enumerate(files, start=1):
            nama = f"Lapangan {idx}"
            defaults = {
                'deskripsi': f'Deskripsi {nama}',
                'harga_per_jam': 50000 + (idx % 5) * 10000
            }
            lap, created = Lapangan.objects.get_or_create(nama=nama, defaults=defaults)
            if created:
                path = os.path.join(seed_dir, fname)
                with open(path, 'rb') as f:
                    lap.gambar.save(fname, File(f), save=True)
                self.stdout.write(self.style.SUCCESS(f'Created {lap.nama} -> {fname}'))
            else:
                self.stdout.write(self.style.WARNING(f'{lap.nama} already exists, skipped'))
        self.stdout.write(self.style.SUCCESS('Done.'))
