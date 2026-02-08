from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from . import db, town


NO_CSRF = {
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
    "UNAUTHENTICATED_USER": None,
}


@override_settings(
    REST_FRAMEWORK=NO_CSRF,
    SESSION_COOKIE_SECURE=False,
    CSRF_COOKIE_SECURE=False,
)
class UserEndpointTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        town.ensure_schema()

    def setUp(self):
        self.client = APIClient()

    def test_create_user(self):
        res = self.client.get('/api/user/me/')
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.data['points'], 0)
        self.assertTrue(res.data['user_id'])

    def test_session_persistence(self):
        res1 = self.client.get('/api/user/me/')
        res2 = self.client.get('/api/user/me/')
        self.assertEqual(res1.data['user_id'], res2.data['user_id'])
        self.assertEqual(res2.status_code, 200)


@override_settings(
    REST_FRAMEWORK=NO_CSRF,
    SESSION_COOKIE_SECURE=False,
    CSRF_COOKIE_SECURE=False,
)
class TownEndpointTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        town.ensure_schema()

    def setUp(self):
        self.client = APIClient()
        self.client.get('/api/user/me/')

    def test_get_town_shape(self):
        res = self.client.get('/api/town/')
        self.assertEqual(res.status_code, 200)
        self.assertIn('town_id', res.data)
        self.assertIn('seed', res.data)
        self.assertIn('tiles', res.data)
        self.assertIn('npcs', res.data)
        self.assertIn('events', res.data)
        self.assertIn('version', res.data)
        self.assertIn('allowed_event_ids', res.data)
        self.assertEqual(len(res.data['tiles']), 20)

    def test_event_requires_session(self):
        fresh = APIClient()
        res = fresh.post('/api/town/event/', {'event_id': 'read_sign_gate', 'payload': {}}, format='json')
        self.assertEqual(res.status_code, 401)

    def test_event_adjacency_validation(self):
        snapshot = self.client.get('/api/town/').data
        res = self.client.post(
            '/api/town/event/',
            {
                'event_id': 'read_sign_gate',
                'version': snapshot['version'],
                'payload': {
                    'player_position': {'x': 20, 'y': 10},
                    'target_position': {'x': 3, 'y': 2},
                },
            },
            format='json',
        )
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.data['error_code'], 'invalid_position')

    def test_one_time_event_idempotent(self):
        snapshot = self.client.get('/api/town/').data
        first = self.client.post(
            '/api/town/event/',
            {
                'event_id': 'open_chest_herb',
                'version': snapshot['version'],
                'payload': {
                    'player_position': {'x': 26, 'y': 3},
                    'target_position': {'x': 27, 'y': 3},
                },
            },
            format='json',
        )
        self.assertEqual(first.status_code, 200)
        self.assertEqual(first.data['event_result']['message_key'], 'event.chest_herb_opened')

        second = self.client.post(
            '/api/town/event/',
            {
                'event_id': 'open_chest_herb',
                'version': first.data['snapshot']['version'],
                'payload': {
                    'player_position': {'x': 26, 'y': 3},
                    'target_position': {'x': 27, 'y': 3},
                },
            },
            format='json',
        )
        self.assertEqual(second.status_code, 200)
        self.assertTrue(second.data['idempotent'])

    def test_stale_version_rejected(self):
        snapshot = self.client.get('/api/town/').data
        self.client.post(
            '/api/town/event/',
            {
                'event_id': 'read_sign_gate',
                'version': snapshot['version'],
                'payload': {
                    'player_position': {'x': 2, 'y': 2},
                    'target_position': {'x': 3, 'y': 2},
                },
            },
            format='json',
        )
        stale = self.client.post(
            '/api/town/event/',
            {
                'event_id': 'read_sign_plaza',
                'version': snapshot['version'],
                'payload': {
                    'player_position': {'x': 15, 'y': 10},
                    'target_position': {'x': 16, 'y': 10},
                },
            },
            format='json',
        )
        self.assertEqual(stale.status_code, 409)
        self.assertEqual(stale.data['error_code'], 'stale_client')

    def test_fetch_quest_flow_items_and_flags(self):
        start = self.client.get('/api/town/').data

        self.client.post(
            '/api/town/event/',
            {
                'event_id': 'talk_npc_lyra',
                'version': start['version'],
                'payload': {
                    'player_position': {'x': 6, 'y': 2},
                    'target_position': {'x': 6, 'y': 3},
                },
            },
            format='json',
        )

        after_chest = self.client.post(
            '/api/town/event/',
            {
                'event_id': 'open_chest_herb',
                'version': self.client.get('/api/town/').data['version'],
                'payload': {
                    'player_position': {'x': 26, 'y': 3},
                    'target_position': {'x': 27, 'y': 3},
                },
            },
            format='json',
        )
        self.assertEqual(after_chest.status_code, 200)

        lyra_turnin = self.client.post(
            '/api/town/event/',
            {
                'event_id': 'talk_npc_lyra',
                'version': after_chest.data['snapshot']['version'],
                'payload': {
                    'player_position': {'x': 6, 'y': 2},
                    'target_position': {'x': 6, 'y': 3},
                },
            },
            format='json',
        )
        self.assertEqual(lyra_turnin.status_code, 200)
        self.assertEqual(lyra_turnin.data['event_result']['message_key'], 'event.lyra.quest_complete')

        final_snapshot = lyra_turnin.data['snapshot']
        flags = set(final_snapshot['player_state']['flags'])
        self.assertIn('herb_quest_started', flags)
        self.assertIn('herb_collected', flags)
        self.assertIn('herb_turned_in', flags)

        item_ids = {item['item_id'] for item in final_snapshot['player_state']['items'] if item['qty'] > 0}
        self.assertIn('moon_badge', item_ids)


@override_settings(SESSION_COOKIE_SECURE=False, CSRF_COOKIE_SECURE=False)
class CsrfTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        town.ensure_schema()

    def setUp(self):
        self.client = APIClient(enforce_csrf_checks=True)

    def test_get_town_returns_csrf_cookie(self):
        res = self.client.get('/api/town/')
        self.assertIn('agame_csrf', res.cookies)

    def test_post_event_without_csrf_rejected(self):
        snapshot = self.client.get('/api/town/').data
        res = self.client.post(
            '/api/town/event/',
            {
                'event_id': 'read_sign_gate',
                'version': snapshot['version'],
                'payload': {
                    'player_position': {'x': 2, 'y': 2},
                    'target_position': {'x': 3, 'y': 2},
                },
            },
            format='json',
        )
        self.assertEqual(res.status_code, 403)


@override_settings(
    REST_FRAMEWORK=NO_CSRF,
    SESSION_COOKIE_SECURE=False,
    CSRF_COOKIE_SECURE=False,
)
class DbRulesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        town.ensure_schema()

    def setUp(self):
        self.client = APIClient()
        self.client.get('/api/user/me/')

    def test_item_types_seeded(self):
        count = db.fetch_one('SELECT COUNT(*) FROM item_types')[0]
        self.assertGreaterEqual(count, 6)

    def test_town_row_created(self):
        self.client.get('/api/town/')
        user_id = self.client.session['user_id']
        count = db.fetch_one('SELECT COUNT(*) FROM player_towns WHERE user_id = %s', [user_id])[0]
        self.assertEqual(count, 1)
