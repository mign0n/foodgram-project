import csv
import json

from django.core.management.base import BaseCommand, CommandParser
from recipes import models


class Command(BaseCommand):
    def handle(self, *args: tuple, **options: dict[str, str]) -> None:
        del args
        with open(
            options.get('file', ''),  # type: ignore
            encoding='utf-8',
        ) as file:
            if not options.get('json'):
                contents = csv.DictReader(
                    file,
                    fieldnames=('name', 'measurement_unit'),
                )
            else:
                contents = json.load(file)
            for row in contents:
                models.Ingredient.objects.get_or_create(**row)  # type: ignore

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            '-f',
            '--file',
            action='store',
            help='Filepath to load, e.g. "data/ingredients.csv".',
            required=True,
            type=str,
        )
        parser.add_argument(
            '--json',
            action='store_true',
            help='JSON file format.',
        )
