import os
# pyrefly: ignore [missing-import]
import django
# pyrefly: ignore [missing-import]
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ged_universitaire.settings')
django.setup()

output_file = 'data_migration_final.json'
print(f"Extraction des données vers {output_file}...")

with open(output_file, 'w', encoding='utf-8') as f:
    call_command('dumpdata', exclude=['contenttypes', 'auth.Permission'], indent=2, stdout=f)

print("Extraction terminée avec succès en UTF-8.")
