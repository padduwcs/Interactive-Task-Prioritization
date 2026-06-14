"""Interactive merge sort logic for task prioritization."""

import math


def estimate_merge_sort_comparisons(n: int) -> int:
    """Estimate the maximum number of comparisons for merge sort on n items."""
    if n <= 1:
        return 0
    depth = math.ceil(math.log2(n))
    return n * depth - (1 << depth) + 1


def interactive_merge_sort(tasks):
    """
    Generator-based merge sort that yields task pairs for comparison.

    Each time a comparison is required, this generator yields a tuple
    (task_left, task_right). The caller must send back the chosen task
    via generator.send(chosen_task) before sorting continues.
    """
    if len(tasks) <= 1:
        return tasks

    mid = len(tasks) // 2
    left = yield from interactive_merge_sort(tasks[:mid])
    right = yield from interactive_merge_sort(tasks[mid:])

    merged = []
    i = 0
    j = 0

    while i < len(left) and j < len(right):
        winner = yield (left[i], right[j])

        if winner == left[i]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1

    if i < len(left):
        merged.extend(left[i:])
    if j < len(right):
        merged.extend(right[j:])

    return merged
