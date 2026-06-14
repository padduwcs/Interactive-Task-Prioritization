import unittest

from sorter_logic import estimate_merge_sort_comparisons, interactive_merge_sort


def run_sort(tasks, rank):
    generator = interactive_merge_sort(tasks)
    comparisons = 0

    try:
        pair = next(generator)
        while True:
            comparisons += 1
            left, right = pair
            chosen = left if rank[left[1]] < rank[right[1]] else right
            pair = generator.send(chosen)
    except StopIteration as stop:
        return stop.value, comparisons


class InteractiveMergeSortTests(unittest.TestCase):
    def test_estimated_comparisons_for_small_inputs(self):
        self.assertEqual(estimate_merge_sort_comparisons(0), 0)
        self.assertEqual(estimate_merge_sort_comparisons(1), 0)
        self.assertEqual(estimate_merge_sort_comparisons(2), 1)
        self.assertEqual(estimate_merge_sort_comparisons(3), 3)
        self.assertEqual(estimate_merge_sort_comparisons(4), 5)

    def test_empty_and_single_item_finish_without_comparisons(self):
        for tasks in ([], [(0, 'A')]):
            with self.subTest(tasks=tasks):
                generator = interactive_merge_sort(tasks)
                with self.assertRaises(StopIteration) as context:
                    next(generator)
                self.assertEqual(context.exception.value, tasks)

    def test_sorts_by_user_choices(self):
        tasks = [(0, 'A'), (1, 'B'), (2, 'C'), (3, 'D')]
        rank = {'D': 0, 'B': 1, 'A': 2, 'C': 3}

        sorted_tasks, comparisons = run_sort(tasks, rank)

        self.assertEqual([task for _, task in sorted_tasks], ['D', 'B', 'A', 'C'])
        self.assertLessEqual(comparisons, estimate_merge_sort_comparisons(len(tasks)))


if __name__ == '__main__':
    unittest.main()
