import math

import numpy as np
import pytest

from kitt.dataloading import BatchGenerator, EagerGenerator, MappingSequence


class TestGenerator(BatchGenerator):
    def __init__(self, dataset, batch_size: int):
        super().__init__(dataset, batch_size)

    def load_sample(self, index):
        return [1, 2, 3, 4], [[1, 2, 3], [3, 4, 5]]


def check_test_generator(generator, length):
    batch_size = generator.batch_size
    assert len(generator) == math.ceil(length / batch_size)

    remaining = length
    for (x, y) in generator:
        expected_size = min(remaining, batch_size)
        assert x.shape == (expected_size, 4)
        assert y.shape == (expected_size, 2, 3)
        remaining -= expected_size


@pytest.mark.parametrize("batch_size", range(1, 9))
def test_batch_size(batch_size):
    dataset = list(range(7))
    generator = TestGenerator(len(dataset), batch_size)
    check_test_generator(generator, len(dataset))


def test_eager_loading():
    batch_size = 2
    dataset = list(range(7))
    generator = EagerGenerator(TestGenerator(len(dataset), batch_size), 3)
    check_test_generator(generator, len(dataset))


def test_mapping():
    batches = [
        ([1, 2, 3], [8, 3, 4, 5]),
        ([50, 2, 13], [12, 3, 10, 13]),
        ([8, 3, 81], [36, 10, 0, 3]),
        ([10, 5, 3], [18, 1, 14, 25]),
        ([51, 4, 2], [5, 2, 2, 6]),
    ]

    class Generator(BatchGenerator):
        def __init__(self):
            super().__init__(len(batches), batch_size=2, seed=0)

        def load_sample(self, index):
            return batches[index]

    def map_x(batch):
        batch = np.array(batch)
        return np.array(list(item / 2 for item in batch))

    def map_y(batch):
        batch = np.array(batch)
        return np.array(list(item * 2 for item in batch))

    generator = Generator()
    mapping = MappingSequence(generator, map_x, map_y)

    xs = []
    ys = []
    for x, y in mapping:
        xs.extend(x)
        ys.extend(y)

    assert np.array_equal(
        np.array(xs),
        [
            [4.0, 1.5, 40.5],
            [0.5, 1.0, 1.5],
            [25.0, 1.0, 6.5],
            [5.0, 2.5, 1.5],
            [25.5, 2.0, 1.0],
        ],
    )
    assert np.array_equal(
        np.array(ys),
        [
            [72, 20, 0, 6],
            [16, 6, 8, 10],
            [24, 6, 20, 26],
            [36, 2, 28, 50],
            [10, 4, 4, 12],
        ],
    )
