import uuid
from django.db import migrations, models


def gen_uuid(apps, schema_editor):
    JobSeekerProfile = apps.get_model('accounts', 'JobSeekerProfile')
    for row in JobSeekerProfile.objects.all():
        row.uuid = uuid.uuid4()
        row.save(update_fields=['uuid'])


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_otpverification'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobseekerprofile',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, null=True, editable=False),
        ),
        migrations.RunPython(gen_uuid, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name='jobseekerprofile',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True),
        ),
    ]
