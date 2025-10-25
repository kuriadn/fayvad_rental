# Generated manually for maintenance satisfaction feedback fields

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('maintenance', '0002_alter_maintenancerequest_created_by_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='maintenancerequest',
            name='feedback_date',
            field=models.DateTimeField(blank=True, null=True, help_text='When tenant provided feedback'),
        ),
        migrations.AddField(
            model_name='maintenancerequest',
            name='tenant_feedback',
            field=models.TextField(blank=True, help_text="Tenant's feedback on the maintenance resolution", null=True),
        ),
        migrations.AddField(
            model_name='maintenancerequest',
            name='tenant_satisfaction_rating',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(1, 'Very Dissatisfied'), (2, 'Dissatisfied'), (3, 'Neutral'), (4, 'Satisfied'), (5, 'Very Satisfied')], help_text="Tenant's satisfaction rating (1-5 scale)", null=True),
        ),
    ]
