# gallery/management/commands/load_lapangan.py
from django.core.management.base import BaseCommand
from django.core.files import File
from django.utils.text import slugify
from gallery.models import Lapangan
import os
import uuid

class Command(BaseCommand):
    help = "Load lapangan dari folder media/seed (satu file => satu Lapangan)."

    def handle(self, *args, **options):
        folder_path = os.path.join('media', 'seed')
        if not os.path.exists(folder_path):
            self.stdout.write(self.style.ERROR(f"Folder not found: {folder_path}"))
            return

        files = sorted([f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
        created = 0
        for i, filename in enumerate(files, start=1):
            nama = f"Lapangan {i}"
            # buat slug unik (tambah uuid kalau perlu)
            base_slug = slugify(nama) or f"lapangan-{i}"
            slug = base_slug
            # jika slug sudah ada, tambahkan suffix unik
            counter = 1
            while Lapangan.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            # Cek kalau record dengan nama ini sudah ada -> skip
            if Lapangan.objects.filter(nama=nama).exists():
                self.stdout.write(self.style.WARNING(f"{nama} sudah ada, dilewati."))
                continue

            lap = Lapangan(
                nama=nama,
                slug=slug,
                deskripsi="Deskripsi singkat lapangan.",
                harga_per_jam=50000 + (i % 5) * 10000,
                fasilitas="Toilet, Parkir"
            )
            lap.save()  # simpan dulu supaya fk & path bisa dipakai

            # simpan file image ke field ImageField
            fpath = os.path.join(folder_path, filename)
            try:
                with open(fpath, 'rb') as f:
                    lap.gambar.save(filename, File(f), save=True)
                created += 1
                self.stdout.write(self.style.SUCCESS(f"Created: {nama} <- {filename}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error saving image {filename}: {e}"))
                lap.delete()

        self.stdout.write(self.style.SUCCESS(f"Done. Created {created} lapangan."))
