import uuid
from django.db import migrations, models


def gen_uuids(apps, schema_editor):
    for model_name in ['User', 'Skill', 'JobSeekerSkill', 'Education', 'Experience']:
        Model = apps.get_model('accounts', model_name)
        for row in Model.objects.all():
            row.uuid = uuid.uuid4()
            row.save(update_fields=['uuid'])


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_jobseekerprofile_uuid'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, null=True, editable=False),
        ),
        migrations.AddField(
            model_name='skill',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, null=True, editable=False),
        ),
        migrations.AddField(
            model_name='jobseekerskill',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, null=True, editable=False),
        ),
        migrations.AddField(
            model_name='education',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, null=True, editable=False),
        ),
        migrations.AddField(
            model_name='experience',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, null=True, editable=False),
        ),
        migrations.RunPython(gen_uuids, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name='user',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True),
        ),
        migrations.AlterField(
            model_name='skill',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True),
        ),
        migrations.AlterField(
            model_name='jobseekerskill',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True),
        ),
        migrations.AlterField(
            model_name='education',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True),
        ),
        migrations.AlterField(
            model_name='experience',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True),
        ),
    ]
