from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("orders", "0001_initial")]
    operations = [
        migrations.AddField(
            model_name="order",
            name="external_reference",
            field=models.CharField(default="", max_length=20, unique=True),
            preserve_default=False,
        ),
    ]
