import uuid

from django.db import migrations


def convert_tag_ids_to_uuid(apps, schema_editor):
    connection = schema_editor.connection

    with connection.cursor() as cursor:
        cursor.execute("SELECT id FROM main_tag")
        tag_ids = [row[0] for row in cursor.fetchall()]

        for old_id in tag_ids:
            try:
                uuid.UUID(str(old_id))
            except (ValueError, AttributeError, TypeError):
                new_id = uuid.uuid4().hex
                cursor.execute(
                    "UPDATE main_project_tags SET tag_id = %s WHERE tag_id = %s",
                    [new_id, old_id],
                )
                cursor.execute(
                    "UPDATE main_skill_tags SET tag_id = %s WHERE tag_id = %s",
                    [new_id, old_id],
                )
                cursor.execute(
                    "UPDATE main_tag SET id = %s WHERE id = %s",
                    [new_id, old_id],
                )


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0005_alter_tag_id"),
    ]

    operations = [
        migrations.RunPython(convert_tag_ids_to_uuid, migrations.RunPython.noop),
    ]
