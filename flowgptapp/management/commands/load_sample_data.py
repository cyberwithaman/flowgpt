from django.core.management.base import BaseCommand
from flowgptapp.sample_data import create_sample_data


class Command(BaseCommand):
    help = 'Loads sample data for FlowGPT application'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.MIGRATE_HEADING('Loading sample data for FlowGPT...'))
        
        try:
            create_sample_data()
            self.stdout.write(self.style.SUCCESS('Sample data loaded successfully.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error loading sample data: {str(e)}')) 