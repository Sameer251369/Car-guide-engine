from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0006_alter_vehicleimage_image_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehicleimage',
            name='image_type',
            field=models.CharField(
                choices=[
                    ('front', 'Front side'),
                    ('exterior', 'Exterior / side'),
                    ('interior', 'Interior'),
                    ('rear', 'Backside / rear'),
                ],
                default='front',
                help_text='View shown for this vehicle image.',
                max_length=20,
            ),
        ),
    ]