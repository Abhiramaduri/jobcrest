import uuid
from django.db import migrations, models


def gen_uuids(apps, schema_editor):
    for model_name in ['Company', 'EmployerProfile']:
        Model = apps.get_model('companies', model_name)
        for row in Model.objects.all():
            row.uuid = uuid.uuid4()
            row.save(update_fields=['uuid'])


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, null=True, editable=False),
        ),
        migrations.AddField(
            model_name='employerprofile',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, null=True, editable=False),
        ),
        migrations.RunPython(gen_uuids, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name='company',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True),
        ),
        migrations.AlterField(
            model_name='employerprofile',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True),
        ),
    ]
