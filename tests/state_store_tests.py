import json
import unittest
import uuid
from pathlib import Path

from state_store import TaskStateStore


WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
TEST_STATE_DIR = WORKSPACE_ROOT / 'tests' / '.tmp_state'


class TaskStateStoreTests(unittest.TestCase):
    def setUp(self):
        TEST_STATE_DIR.mkdir(parents=True, exist_ok=True)

    def state_path(self, name: str) -> Path:
        return TEST_STATE_DIR / f'{uuid.uuid4().hex}_{name}'

    def test_saves_and_loads_result_state(self):
        store = TaskStateStore(self.state_path('save_load_state.json'))

        saved = store.save_result([(2, 'Write proposal'), (0, 'Pay invoice')], [False, True])

        self.assertTrue(saved)
        self.assertEqual(
            store.load(),
            {
                'version': 1,
                'view': 'result',
                'sorted_tasks': [
                    {'text': 'Write proposal', 'done': False},
                    {'text': 'Pay invoice', 'done': True},
                ],
            },
        )

    def test_delete_removes_saved_state(self):
        store = TaskStateStore(self.state_path('delete_state.json'))
        store.save_result([(0, 'Task')])

        self.assertTrue(store.delete())
        loaded_state = store.load()
        self.assertTrue(loaded_state is None or loaded_state['sorted_tasks'] == [])

    def test_invalid_state_is_ignored(self):
        state_path = self.state_path('invalid_state.json')
        state_path.write_text(json.dumps({'version': 999}), encoding='utf-8')

        self.assertIsNone(TaskStateStore(state_path).load())


if __name__ == '__main__':
    unittest.main()
