"""
Django management command to enrich localities with AI analysis.

Usage:
    python manage.py enrich_localities              # Enrich all missing profiles
    python manage.py enrich_localities --id=5       # Enrich specific locality
    python manage.py enrich_localities --all        # Force re-enrich all
"""

from django.core.management.base import BaseCommand
from django.db.models import Q
from properties.models import Locality
from properties.tasks import enrich_locality_pipeline


class Command(BaseCommand):
    help = 'Queue Celery tasks to enrich localities with AI analysis'

    def add_arguments(self, parser):
        parser.add_argument(
            '--id',
            type=int,
            help='Enrich specific locality by ID',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Re-enrich all localities (including those already analyzed)',
        )

    def handle(self, *args, **options):
        if options['id']:
            # Enrich specific locality
            try:
                locality = Locality.objects.get(id=options['id'])
                self.stdout.write(f"Queuing task for: {locality.name} (ID: {locality.id})")
                task_id = enrich_locality_pipeline.delay(locality.id)
                self.stdout.write(
                    self.style.SUCCESS(f"✓ Task queued: {task_id}")
                )
            except Locality.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"✗ Locality with ID {options['id']} not found")
                )

        elif options['all']:
            # Re-enrich all localities
            localities = Locality.objects.all()
            count = localities.count()
            self.stdout.write(f"Queuing tasks for {count} localities...")
            
            for locality in localities:
                task_id = enrich_locality_pipeline.delay(locality.id)
                self.stdout.write(f"  → {locality.name}: {task_id}")
            
            self.stdout.write(
                self.style.SUCCESS(f"✓ Queued {count} tasks")
            )

        else:
            # Enrich localities without profiles
            localities = Locality.objects.filter(profile__isnull=True)
            count = localities.count()
            
            if count == 0:
                self.stdout.write(
                    self.style.SUCCESS("✓ All localities already enriched!")
                )
                return
            
            self.stdout.write(f"Queuing tasks for {count} localities without analysis...")
            
            for locality in localities:
                task_id = enrich_locality_pipeline.delay(locality.id)
                self.stdout.write(f"  → {locality.name} (ID: {locality.id}): {task_id}")
            
            self.stdout.write(
                self.style.SUCCESS(f"✓ Queued {count} tasks")
            )
            self.stdout.write("Tasks will be processed by GitHub Actions every 5 minutes")
