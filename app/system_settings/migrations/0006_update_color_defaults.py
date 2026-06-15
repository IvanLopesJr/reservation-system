from django.db import migrations


def update_colors(apps, schema_editor):
    SystemSettings = apps.get_model('system_settings', 'SystemSettings')
    settings = SystemSettings.objects.first()
    if settings:
        if settings.primary_color == '#0d6efd':
            settings.primary_color = '#4f46e5'
        if settings.secondary_color == '#6c757d':
            settings.secondary_color = '#f43f5e'
        if settings.background_color == '#f8f9fa':
            settings.background_color = '#f8fafc'
        if settings.navbar_bg_color == '#0d6efd':
            settings.navbar_bg_color = '#4f46e5'
        settings.save()


class Migration(migrations.Migration):

    dependencies = [
        ('system_settings', '0005_alter_systemsettings_background_color_and_more'),
    ]

    operations = [
        migrations.RunPython(update_colors, migrations.RunPython.noop),
    ]
