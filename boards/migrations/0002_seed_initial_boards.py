from django.db import migrations


INITIAL_BOARDS = [
    {'slug': 'random', 'name': 'Random', 'description': 'Wszystko i nic - ogólna tablica.', 'nsfw': False},
    {'slug': 'tech', 'name': 'Technologia', 'description': 'Programowanie, sprzęt, IT.', 'nsfw': False},
    {'slug': 'gry', 'name': 'Gry', 'description': 'Gry wideo i planszowe.', 'nsfw': False},
    {'slug': 'hobby', 'name': 'Hobby', 'description': 'Zainteresowania i pasje.', 'nsfw': False},
]


def seed_boards(apps, schema_editor):
    Board = apps.get_model('boards', 'Board')
    for data in INITIAL_BOARDS:
        Board.objects.get_or_create(slug=data['slug'], defaults=data)


def unseed_boards(apps, schema_editor):
    Board = apps.get_model('boards', 'Board')
    Board.objects.filter(slug__in=[b['slug'] for b in INITIAL_BOARDS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('boards', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_boards, unseed_boards),
    ]
