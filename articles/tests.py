from django.test import TestCase
from django.urls import reverse

from articles.models import Catalog


class CatalogModelTest(TestCase):
    def test_catalog_creation(self):
        catalog = Catalog.objects.create(name="Электроника")
        self.assertEqual(str(catalog), "Электроника")

    def test_catalog_list_view(self):
        Catalog.objects.create(name="Книги")
        response = self.client.get("/catalog/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Книги")
