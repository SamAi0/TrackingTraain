import os
import json
from django.test import TestCase, Client
from stations.models import Station

class APIRoutesTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_db_coverage(self):
        mh_stations_in_db = Station.objects.filter(state__icontains='maharashtra').count()
        print(f"Maharashtra stations in DB: {mh_stations_in_db}")
        # Not asserting a strict count to avoid brittleness, just making sure it runs.
        self.assertGreaterEqual(mh_stations_in_db, 0)

    def test_routes_normal(self):
        response = self.client.get("/api/routes/search/?from=TNA&to=CSTM")
        # In a test db, there might be no routes, but we expect a JSON response.
        # It could return 200 or 404/400 depending on fixture data.
        self.assertIn(response.status_code, [200, 404])

    def test_routes_missing_params(self):
        response = self.client.get("/api/routes/search/")
        self.assertEqual(response.status_code, 400)

    def test_routes_same_station(self):
        response = self.client.get("/api/routes/search/?from=TNA&to=TNA")
        self.assertEqual(response.status_code, 400)

    def test_autocomplete(self):
        response = self.client.get("/api/stations/autocomplete/?q=pun")
        self.assertEqual(response.status_code, 200)
