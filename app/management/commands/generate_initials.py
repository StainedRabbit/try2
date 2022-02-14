import csv
from itertools import product
from django.core.management.base import BaseCommand
from django.utils import timezone

from app.models.product import Product

from django.apps import apps

from app.models.user import User


class Command(BaseCommand):
    help = "Generate initial data for products and users. This should be run only once."

    def handle(self, *args, **kwargs):

        time = timezone.now().strftime("%X")
        self.stdout.write(time)
        app_path = apps.get_app_config("app").path

        folder_path = app_path + "/fixtures/initials/"

        self.stdout.write("Generating initial products...")

        with open(folder_path + "products.csv", "r") as file:
            data = csv.reader(file)
            for record in data:
                product = Product.objects.create(name=record[0])
                price = product.prices.first()
                price.amount = record[2]
                price.save()
                product.adjustments.create(quantity=record[1])
                print(record)

        self.stdout.write(
            self.style.SUCCESS(f"Generated {Product.objects.count()} products.")
        )

        self.stdout.write("Generating initial users...")

        import codecs

        with codecs.open(
            folder_path + "members.csv", encoding="utf-8", errors="ignore"
        ) as file:
            data = csv.reader(file)
            for r in data:
                names = r[0].split(", ")
                print(names)
                if not r[1]:
                    email = "".join(names).replace(" ", "") + "@mccoop.com"
                    # print(email)
                else:
                    email = r[1]
                password = User.objects.make_random_password()
                member = User.objects.create(
                    last_name=names[0], first_name=names[1], email=email
                )
                member.set_password(password)
                member.save()

        self.stdout.write(
            self.style.SUCCESS(f"Generated {User.objects.count()} users.")
        )
