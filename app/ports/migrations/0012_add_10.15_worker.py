from django.db import migrations


def add_new_builder(apps, schema_editor):
    Builder = apps.get_model('ports', 'Builder')
    Builder.objects.create(name='10.15_x86_64', display_name='10.15')


class Migration(migrations.Migration):

    dependencies = [
        ('ports', '0011_populate_display_name.py'),
    ]

    operations = [
        migrations.RunPython(add_new_builder),
    ]
