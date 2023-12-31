# Generated by Django 4.2.4 on 2023-09-14 10:59

from django.db import migrations, models
import django.db.models.deletion
import froala_editor.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Bot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Date of creation')),
                ('updated_at', models.DateTimeField(auto_now=True, null=True, verbose_name='Date of update')),
                ('bot_type', models.CharField(choices=[('discord', 'Discord'), ('telegram', 'Telegram')], default='telegram', help_text='Available types: Discord; Telegram', max_length=255, verbose_name='Bot type')),
                ('token', models.CharField(blank=True, help_text='Create a Telegram bot using @BotFather and copy the received token into this field.<br>Token example: 0123456789:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX', max_length=255, null=True, verbose_name='Telegram bot token')),
                ('webhook', models.CharField(blank=True, help_text='Create a Discord webhook using Server Settings > Integrations > Webhooks.<br>Webhook example: https://discord.com/api/webhooks/your-webhook-id/your-webhook-token', max_length=255, null=True, verbose_name='Discord webhook')),
                ('username', models.CharField(blank=True, max_length=255, null=True, verbose_name='Bot username')),
            ],
            options={
                'verbose_name': 'Bot',
                'verbose_name_plural': 'Bots',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Channel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Date of creation')),
                ('updated_at', models.DateTimeField(auto_now=True, null=True, verbose_name='Date of update')),
                ('image', models.ImageField(blank=True, null=True, upload_to='', verbose_name='Image')),
                ('channel_type', models.CharField(choices=[('discord', 'Discord'), ('telegram', 'Telegram')], help_text='Available types: Discord; Telegram', max_length=255, verbose_name='Channel type')),
                ('channel_id', models.BigIntegerField(blank=True, help_text='Insert your channel id', null=True, verbose_name='Channel id')),
                ('server_id', models.BigIntegerField(blank=True, help_text='Insert your discord server id', null=True, verbose_name='Discord server id')),
                ('title', models.CharField(blank=True, help_text='Name retrieved automatically via API', max_length=255, null=True, verbose_name='Channel name')),
                ('description', models.TextField(blank=True, help_text='Description retrieved automatically via API', null=True, verbose_name='Channel description')),
                ('username', models.CharField(blank=True, help_text='Username retrieved automatically via API', null=True, verbose_name='Channel username')),
                ('invite_link', models.CharField(blank=True, help_text='Link retrieved automatically via API', null=True, verbose_name='Channel link')),
                ('is_completed', models.BooleanField(default=False, verbose_name='Is completed')),
                ('bot', models.ForeignKey(help_text='Previously created bot', null=True, on_delete=django.db.models.deletion.SET_NULL, to='poster.bot', verbose_name='Bot')),
            ],
            options={
                'verbose_name': 'Channel',
                'verbose_name_plural': 'Channels',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Date of creation')),
                ('updated_at', models.DateTimeField(auto_now=True, null=True, verbose_name='Date of update')),
                ('post_type', models.CharField(choices=[('audio', 'Audio message'), ('document', 'Document message'), ('gallery_documents', 'Gallery documents'), ('gallery_photos', 'Gallery photos'), ('text', 'Text message'), ('photo', 'Photo message'), ('video', 'Video message'), ('voice', 'Voice message')], help_text='Select post type to continue', max_length=32, verbose_name='Post type')),
                ('audio', models.FileField(blank=True, help_text='Select an audio file to send as a voice message', null=True, upload_to='', verbose_name='Audio file')),
                ('document', models.FileField(blank=True, help_text='', null=True, upload_to='', verbose_name='Document file')),
                ('video', models.FileField(blank=True, help_text='', null=True, upload_to='', verbose_name='Video file')),
                ('photo', models.ImageField(blank=True, help_text='', null=True, upload_to='', verbose_name='Photo file')),
                ('voice', models.FileField(blank=True, help_text='', null=True, upload_to='', verbose_name='Voice file')),
                ('caption', froala_editor.fields.FroalaField(blank=True, help_text='Insert caption (max length 255 symbols)', null=True, verbose_name='Caption')),
                ('message', froala_editor.fields.FroalaField(blank=True, help_text='Enter the text to send it to the channel. The maximum length for one message is 4096 characters', null=True, verbose_name='Message text')),
                ('is_published', models.BooleanField(default=False, verbose_name='Is published')),
                ('channels', models.ManyToManyField(to='poster.channel', verbose_name='Channels')),
            ],
            options={
                'verbose_name': 'Post',
                'verbose_name_plural': 'Posts',
                'ordering': ['-updated_at'],
            },
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_at', models.DateTimeField(auto_now=True, null=True, verbose_name='Date of update')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Date of creation')),
                ('task_id', models.UUIDField(verbose_name='Celery task id')),
                ('task_type', models.CharField(choices=[('create', 'CREATE'), ('update', 'UPDATE'), ('delete', 'DELETE')], help_text='Type of action at which the record was created', max_length=32, null=True, verbose_name='Task type')),
                ('response', models.TextField(help_text='Automatically recorded result of sending a message', null=True, verbose_name='Response data')),
                ('exception', models.TextField(help_text='Automatically detected exception to sending a message', null=True, verbose_name='Exception data')),
                ('channel', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='poster.channel', verbose_name='Channel')),
                ('post', models.ForeignKey(help_text='Original post', null=True, on_delete=django.db.models.deletion.SET_NULL, to='poster.post', verbose_name='Post')),
            ],
            options={
                'verbose_name': 'Task',
                'verbose_name_plural': 'Tasks',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='PostMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Date of creation')),
                ('updated_at', models.DateTimeField(auto_now=True, null=True, verbose_name='Date of update')),
                ('message_id', models.BigIntegerField(verbose_name='Message id')),
                ('channel', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='poster.channel', verbose_name='Channel')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='post',
            name='messages',
            field=models.ManyToManyField(related_name='messages', to='poster.postmessage', verbose_name='Messages'),
        ),
        migrations.CreateModel(
            name='GalleryPhoto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Date of creation')),
                ('updated_at', models.DateTimeField(auto_now=True, null=True, verbose_name='Date of update')),
                ('file', models.ImageField(upload_to='', verbose_name='Photo')),
                ('caption', models.TextField(blank=True, help_text='Insert photo caption', null=True, verbose_name='Photo caption')),
                ('post', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='poster.post', verbose_name='Post')),
            ],
            options={
                'verbose_name': 'Photo',
                'verbose_name_plural': 'Photos',
            },
        ),
        migrations.CreateModel(
            name='GalleryDocument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Date of creation')),
                ('updated_at', models.DateTimeField(auto_now=True, null=True, verbose_name='Date of update')),
                ('file', models.FileField(upload_to='', verbose_name='Document')),
                ('caption', models.TextField(blank=True, help_text='Insert document caption', null=True, verbose_name='Document caption')),
                ('post', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='poster.post', verbose_name='Post')),
            ],
            options={
                'verbose_name': 'Document',
                'verbose_name_plural': 'Documents',
            },
        ),
    ]
