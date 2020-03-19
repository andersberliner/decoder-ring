"""
Module to create a set of simple sample data
"""
import pandas as pd
import numpy as np


I_MAX = 1.0
V_MIN = 2.0
V_MAX = 3.5

# Numver of datapoints per step
N_PER_STEP = 5

STEP_ORDER = [
    (1, 'C'),
    (1, 'RAC'),
    (1, 'D'),
    (1, 'RAD'),
    (2, 'C'),
    (2, 'RAC')
]

STEP_CODE_HASH = {'C': 1, 'RAC': 2, 'D': 3, 'RAD': 4}


def _get_step_dpt_data(last_val, n=N_PER_STEP, **kwargs):
    return last_val + np.arange(1, n + 1)


def _get_dpt_data():
    data = []
    for i, (cyc, step_code) in enumerate(STEP_ORDER):
        if i == 0:
            tmp = _get_step_dpt_data(0)
        else:
            tmp = _get_step_dpt_data(tmp[-1])

        data.append(tmp)

    return data


def _get_step_step_idx_data(last_val, n=N_PER_STEP, step_code=None, **kwargs):
    return [STEP_CODE_HASH.get(step_code)] * n


def _get_stp_data():
    data = []
    for i, (cyc, step_code) in enumerate(STEP_ORDER):
        data.append(_get_step_step_idx_data(None, step_code=step_code))

    return data


def _get_step_cyc_data(last_val, n=N_PER_STEP, cyc=None, **kwargs):
    return [cyc] * n


def _get_cyc_data():
    data = []
    for i, (cyc, step_code) in enumerate(STEP_ORDER):
        data.append(_get_step_cyc_data(None, cyc=cyc))

    return data



# def _get_step_time_data(last_val, n=N_PER_STEP):
#     return 0.5 * _get_step_dpt_data(last_val, n=n)



# def _get_time_data():
#     data = []
#     for i, (cyc, step_code) in enumerate(STEP_ORDER):
#         if i == 0:
#             tmp = _get_step_time_data(0)
#         else:
#             tmp = _get_step_time_data(tmp[-1])

#         data.append(tmp)

#     return data


def _get_step_pot_data(last_val, n=N_PER_STEP, step_code=None, **kwargs):
    if step_code == 'C':
        return np.linspace(V_MIN, V_MAX, n, endpoint=True)
    elif step_code == 'RAC':
        return [V_MAX] * n
    elif step_code == 'D':
        return np.linspace(V_MAX, V_MIN, n, endpoint=True)
    elif step_code == 'RAD':
        return [V_MIN] * n
    else:
        raise Exception("Unknown step_code {}".format(step_code))


def _get_pot_data():
    data = []
    for i, (cyc, step_code) in enumerate(STEP_ORDER):
        data.append(_get_step_pot_data(None, step_code=step_code))

    return data



def _get_step_cur_data(last_val, n=N_PER_STEP, step_code=None, **kwargs):
    if step_code == 'C':
        return [I_MAX] * n
    elif step_code == 'RAC':
        return [0.0] * n
    elif step_code == 'D':
        return [-1.0 * I_MAX] * n
    elif step_code == 'RAD':
        return [0.0] * n
    else:
        raise Exception("Unknown step_code {}".format(step_code))


def _get_cur_data():
    data = []
    for i, (cyc, step_code) in enumerate(STEP_ORDER):
        data.append(_get_step_cur_data(None, step_code=step_code))

    return data


def create_data():
    """Returns Dataframe of sample_data."""

    df = pd.DataFrame(data={
        "dpt": np.hstack(_get_dpt_data()),
        "cyc": np.hstack(_get_cyc_data()),
        "stp": np.hstack(_get_stp_data()),
        "cur": np.hstack(_get_cur_data()),
        "pot": np.hstack(_get_pot_data()),
    })

    df["time"] = df["dpt"] / 2.0
    df["start"] = 170

    return df

