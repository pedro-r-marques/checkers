import unittest

from .webapp import app


class WebappTest(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.client = app.test_client()

    def test_move(self):
        rv = self.client.post('/api/move', json={'player': 1, 'auto': True})
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(len(rv.json), 2)

    def test_get_board(self):
        response = self.client.get('/api/board')
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertEqual(len(data['board']), 24)
        self.assertEqual(data['pieces'], [12, 12])

    def test_auto_play(self):
        for _ in range(8):
            rv = self.client.post(
                '/api/move', json={'player': 2, 'auto': True})
            self.assertEqual(rv.status_code, 200)
            rv = self.client.post(
                '/api/move', json={'player': 1, 'auto': True})
            self.assertEqual(rv.status_code, 200)


if __name__ == '__main__':
    unittest.main()
