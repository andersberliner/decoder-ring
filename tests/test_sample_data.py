"""
Tests of the src.sample_data module.
"""
import numpy as np
import pandas as pd
import pytest
from collections import namedtuple

# Relative imports
from src import sample_data


SampleDataParameters = namedtuple("SampleDataParameters", ["step_order", "n",
        "i_max", "v_min", "v_max"])


@pytest.fixture()
def small_sample_conditions():
    """Returns a step_order and number of dpts per step, etc for testing."""
    n = 3
    step_order = [
        (1, 'C'),
        (1, 'RAC'),
        (2, 'D')
    ]

    return SampleDataParameters(step_order=step_order, n=n, i_max=1, v_min=2,
            v_max=3)


@pytest.fixture()
def small_sample_data():
    """Returns a dataframe of expected sample_data.

    Notes
    -----
    Complies with parameters in small_sample_conditions.
    """
    return pd.DataFrame(data={
        "dpt": [1, 2, 3, 4, 5, 6, 7, 8, 9],
        "cyc": [1, 1, 1, 1, 1, 1, 2, 2, 2],
        "stp": [1, 1, 1, 2, 2, 2, 3, 3, 3],
        "cur": [1.0, 1.0, 1.0, 0.0, 0.0, 0.0, -1.0, -1.0, -1.0],
        "pot": [2.0, 2.5, 3.0, 3.0, 3.0, 3.0, 3.0, 2.5, 2.0],
        "time": [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5],
        "start": [170] * 9,
    })


@pytest.mark.parametrize(
    "last_val,ndpts,expected",
    [
        (5, 3, np.array([6, 7, 8])),
        (1, 2, np.array([2, 3])),
    ]
)
def test_get_step_dpt_data(last_val,ndpts,expected):
    """Tests the _get_step_dpt_data - for building dpt vals in a step."""
    assert (sample_data._get_step_dpt_data(last_val, ndpts) == expected).all()


def test_get_dpt_data(small_sample_conditions, small_sample_data):
    """Tests the _get_dpt_data method."""
    assert (sample_data._get_dpt_data(small_sample_conditions.step_order,
            small_sample_conditions.n) == small_sample_data["dpt"].values).all()

def test_create_data(small_sample_conditions, small_sample_data):
    """Tests the create_data method."""
    actual = sample_data.create_data(
        step_order=small_sample_conditions.step_order,
        n=small_sample_conditions.n,
        v_min=small_sample_conditions.v_min,
        v_max=small_sample_conditions.v_max,
        i_max=small_sample_conditions.i_max,
    )

    assert (actual == small_sample_data).all().all()
