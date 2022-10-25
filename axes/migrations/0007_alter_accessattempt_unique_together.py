# Generated by Django 3.2.7 on 2021-09-13 15:16

from django.db import migrations
from django.db.models import Count


def deduplicate_attempts(apps, schema_editor):
    AccessAttempt = apps.get_model("axes", "AccessAttempt")
    db_alias = schema_editor.connection.alias
    duplicated_attempts = (
        AccessAttempt.objects.using(db_alias)
        .values("username", "user_agent", "ip_address")
        .annotate(Count("id"))
        .order_by()
        .filter(id__count__gt=1)
    )

    for attempt in duplicated_attempts:
        redundant_attempts = AccessAttempt.objects.using(db_alias).filter(
            username=attempt["username"],
            user_agent=attempt["user_agent"],
            ip_address=attempt["ip_address"],
        )[1:]
        for redundant_attempt in redundant_attempts:
            redundant_attempt.delete(using=db_alias)


class Migration(migrations.Migration):

    dependencies = [
        ("axes", "0006_remove_accesslog_trusted"),
    ]

    operations = [
        migrations.RunPython(deduplicate_attempts),
        migrations.AlterUniqueTogether(
            name="accessattempt",
            unique_together={("username", "ip_address", "user_agent")},
        ),
    ]
