from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Loads sample data and runs the demo in a single command'

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING('Setting up FlowGPT sample data and running demo'))
        
        # First load the sample data
        self.stdout.write(self.style.MIGRATE_HEADING('Step 1: Loading sample data...'))
        call_command('load_sample_data')
        
        # Then run the demo
        self.stdout.write(self.style.MIGRATE_HEADING('Step 2: Running demo...'))
        call_command('run_demo')
        
        self.stdout.write(self.style.SUCCESS('Setup and demo completed successfully!'))
        self.stdout.write(self.style.MIGRATE_HEADING('You can now access the admin dashboard at /admin/dashboard/'))
        self.stdout.write('Default admin credentials (if you created a superuser):\n')
        self.stdout.write('  - Username: admin\n')
        self.stdout.write('  - Password: (the one you set during setup)\n') 