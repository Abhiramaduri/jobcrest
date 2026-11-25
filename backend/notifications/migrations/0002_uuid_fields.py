import uuid
from django.db import migrations, models


def gen_uuids(apps, schema_editor):
    Notification = apps.get_model('notifications', 'Notification')
    for row in Notification.objects.all():
        row.uuid = uuid.uuid4()
        row.save(update_fields=['uuid'])


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, null=True, editable=False),
        ),
        migrations.RunPython(gen_uuids, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name='notification',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True),
        ),
    ]
