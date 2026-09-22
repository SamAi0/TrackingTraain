import os
import sys
import ijson
import time
from django.core.management.base import BaseCommand
from django.core.serializers.python import Deserializer
from django.db import transaction, connection
from django.apps import apps

class Command(BaseCommand):
    help = 'Imports large JSON fixtures into the database using chunked atomic transactions.'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='The JSON fixture file to import')
        parser.add_argument('--batch-size', type=int, default=5000, help='Number of records to process per transaction')

    def handle(self, *args, **options):
        json_file = options['json_file']
        batch_size = options['batch_size']
        
        self.stdout.write(self.style.SUCCESS(f"Starting chunked import from {json_file} (Batch Size: {batch_size})"))
        
        if not os.path.exists(json_file):
            self.stderr.write(self.style.ERROR(f"File {json_file} does not exist."))
            sys.exit(1)

        # Basic check to ensure tables are empty
        models_to_check = [
            'stations.Station', 'trains.Train', 'routes.Route', 'routes.RouteStation', 'schedules.Schedule',
            'accounts.User', 'bookings.Booking', 'pnr.PNR', 'pnr.Ticket', 'bookings.Invoice',
            'bookings.FareRule', 'bookings.Payment', 'bookings.SystemNotification'
        ]
        total_existing = 0
        for model_name in models_to_check:
            model = apps.get_model(model_name)
            total_existing += model.objects.count()
            
        if total_existing > 0:
            self.stderr.write(self.style.ERROR(f"Database is not empty! Found {total_existing} existing records. Aborting import."))
            sys.exit(1)

        batch = []
        batch_num = 1
        total_processed = 0
        
        with open(json_file, 'rb') as f:
            objects = ijson.items(f, 'item')
            for obj in objects:
                batch.append(obj)
                
                if len(batch) >= batch_size:
                    self._process_batch(batch, batch_num)
                    total_processed += len(batch)
                    batch = []
                    batch_num += 1
                    
            if batch:
                self._process_batch(batch, batch_num)
                total_processed += len(batch)
                
        self.stdout.write(self.style.SUCCESS(f"Import complete! Processed {total_processed} records."))
        
    def _process_batch(self, batch, batch_num):
        self.stdout.write(f"Processing Batch {batch_num} ({len(batch)} records)...")
        retry_count = 0
        max_retries = 3
        while retry_count < max_retries:
            try:
                # Ensure connection is alive (helps if Supabase dropped it)
                connection.ensure_connection()
                
                with transaction.atomic():
                    # Django deserializer processes the dicts and instantiates models
                    deserialized_objects = Deserializer(batch, ignorenonexistent=True)
                    for d_obj in deserialized_objects:
                        d_obj.save()
                return # success
            except Exception as e:
                retry_count += 1
                self.stderr.write(self.style.WARNING(f"Batch {batch_num} failed on attempt {retry_count} with error: {str(e)}"))
                connection.close() # Close connection to force a new one on next attempt
                time.sleep(2)
                
        self.stderr.write(self.style.ERROR(f"Batch {batch_num} permanently failed after {max_retries} attempts."))
        # To aid debugging, print the first object of the batch that failed
        first_obj = batch[0]
        self.stderr.write(self.style.ERROR(f"First object in failed batch: Model={first_obj.get('model')}, PK={first_obj.get('pk')}"))
        sys.exit(1)
