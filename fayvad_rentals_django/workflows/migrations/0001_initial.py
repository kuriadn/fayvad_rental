# Generated migration for workflow models

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0002_staff'),
    ]

    operations = [
        migrations.CreateModel(
            name='WorkflowAuditLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('instance_type', models.CharField(max_length=100)),
                ('instance_id', models.CharField(max_length=50)),
                ('event_type', models.CharField(choices=[('transition', 'State Transition'), ('validation', 'Validation Event'), ('notification', 'Notification Sent'), ('error', 'Error Event'), ('manual', 'Manual Action')], max_length=20)),
                ('event_name', models.CharField(max_length=100)),
                ('old_state', models.CharField(blank=True, max_length=50, null=True)),
                ('new_state', models.CharField(blank=True, max_length=50, null=True)),
                ('user_name', models.CharField(blank=True, max_length=200)),
                ('metadata', models.JSONField(default=dict)),
                ('notes', models.TextField(blank=True)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='accounts.user')),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='WorkflowNotification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notification_type', models.CharField(choices=[('email', 'Email'), ('sms', 'SMS'), ('in_app', 'In-App'), ('push', 'Push Notification')], max_length=20)),
                ('priority', models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('urgent', 'Urgent')], default='medium', max_length=20)),
                ('title', models.CharField(max_length=200)),
                ('message', models.TextField()),
                ('instance_type', models.CharField(max_length=100)),
                ('instance_id', models.CharField(max_length=50)),
                ('event_type', models.CharField(max_length=100)),
                ('event_data', models.JSONField(default=dict)),
                ('sent_at', models.DateTimeField(blank=True, null=True)),
                ('read_at', models.DateTimeField(blank=True, null=True)),
                ('is_sent', models.BooleanField(default=False)),
                ('is_read', models.BooleanField(default=False)),
                ('escalation_level', models.PositiveIntegerField(default=0)),
                ('next_escalation', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='workflow_notifications', to='accounts.user')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='workflowauditlog',
            index=models.Index(fields=['instance_type', 'instance_id'], name='workflows_w_instance__4b7b5e_idx'),
        ),
        migrations.AddIndex(
            model_name='workflowauditlog',
            index=models.Index(fields=['event_type'], name='workflows_w_event_t_9f7b5b_idx'),
        ),
        migrations.AddIndex(
            model_name='workflowauditlog',
            index=models.Index(fields=['timestamp'], name='workflows_w_timesta_5b7b5b_idx'),
        ),
        migrations.AddIndex(
            model_name='workflowauditlog',
            index=models.Index(fields=['user'], name='workflows_w_user_id_5b7b5b_idx'),
        ),
        migrations.AddIndex(
            model_name='workflownotification',
            index=models.Index(fields=['recipient', 'is_read'], name='workflows_w_recipie_4b7b5e_idx'),
        ),
        migrations.AddIndex(
            model_name='workflownotification',
            index=models.Index(fields=['instance_type', 'instance_id'], name='workflows_w_instanc_4b7b5e_idx'),
        ),
        migrations.AddIndex(
            model_name='workflownotification',
            index=models.Index(fields=['is_sent', 'sent_at'], name='workflows_w_is_sent_4b7b5e_idx'),
        ),
        migrations.AddIndex(
            model_name='workflownotification',
            index=models.Index(fields=['next_escalation'], name='workflows_w_next_es_4b7b5e_idx'),
        ),
    ]
