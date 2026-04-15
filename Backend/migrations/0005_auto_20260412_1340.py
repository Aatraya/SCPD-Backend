from django.db import migrations


def create_initial_users(apps, schema_editor):
    # Use apps.get_model to stay compatible with the migration system
    User = apps.get_model("auth", "User")
    Group = apps.get_model("auth", "Group")

    # 1. Create the Mafia Group
    mafia_group, _ = Group.objects.get_or_create(name="Mafia")

    # 2. Create the Police User (Officer)
    if not User.objects.filter(username="officer_vance").exists():
        User.objects.create_user(
            username="officer_vance", password="securepassword123", first_name="Vance"
        )

    # 3. Create the Mafia User (Syndicate)
    if not User.objects.filter(username="tony_pro").exists():
        mafia_user = User.objects.create_user(
            username="tony_pro", password="mafiapassword456"
        )
        mafia_user.groups.add(mafia_group)

    # 4. Optional: Create a Superuser
    if not User.objects.filter(username="admin_aatraya").exists():
        User.objects.create_superuser(
            username="admin_aatraya",
            email="admin@scpd.gov",
            password="adminpassword789",
        )


class Migration(migrations.Migration):
    dependencies = [
        (
            "Backend",
            "0004_remove_criminal_casinos_remove_criminal_criminal_id_and_more",
        ),
    ]

    operations = [
        migrations.RunPython(create_initial_users),
    ]
