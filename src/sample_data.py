"""
Module to create a set of simple sample data
"""
import os
import pandas as pd
import numpy as np

# Relative imports
from .lib import DecoderRingError

# Potential during CC charging and discharging
I_MAX = 1.0

# Min and maximum potentials achieved during CC charging and discharging
V_MIN = 2.0
V_MAX = 3.5

# Number of datapoints per step
N_PER_STEP = 5

# Protocol (cycle, step-type) for sample data
STEP_ORDER = [
    (1, 'C'),
    (1, 'RAC'),
    (1, 'D'),
    (1, 'RAD'),
    (2, 'C'),
    (2, 'RAC')
]

# Step-type code to step-type enum (for encoding).
STEP_CODE_HASH = {'C': 1, 'RAC': 2, 'D': 3, 'RAD': 4}


def _get_step_dpt_data(last_val, n=N_PER_STEP):
    """Returns the dpt-data for a single step.

    Parameters
    ----------
    last_val : int
        Value of last datapoint of previous step.
    n : int
        Number of datapoints per step.

    Returns
    -------
    step_dpt_data : np.array(int)
    """
    return last_val + np.arange(1, n + 1)


def _get_dpt_data(step_order=STEP_ORDER, n=N_PER_STEP):
    """Returns np.array of datapoint number data for sample data.

    Parameters
    ----------
    step_order : list of (int, char)
        List of (Cycle number, step type code) for steps in sample procedure.
    n : int
        Number of datapoints per step.

    Returns
    -------
    dpt_data : np.array(int)
    """
    data = []
    for i, (cyc, step_code) in enumerate(step_order):
        if i == 0:
            tmp = _get_step_dpt_data(0, n=n)
        else:
            tmp = _get_step_dpt_data(tmp[-1], n=n)

        data.append(tmp)

    return np.hstack(data)


def _get_step_stp_idx_data(step_code, n=N_PER_STEP,
        step_code_hash=STEP_CODE_HASH):
    """Returns step-type enum data for each datapoint of a single step.

    Parameters
    ----------
    step_code : char
        1 characater step code for this step
    n : int
        Number of datapoints per step
    step_code_hash : dict
        Step code char to step code enum.

    Returns
    -------
    step_stp_data : np.array(int)
    """
    return step_code_hash[step_code] * np.ones(n)


def _get_stp_data(step_order=STEP_ORDER, n=N_PER_STEP):
    """Returns np.array of step-type enums data for sample data.

    Parameters
    ----------
    step_order : list of (int, char)
        List of (Cycle number, step type code) for steps in sample procedure.
    n : int
        Number of datapoints per step.

    Returns
    -------
    stp_data : np.array(int)
    """
    return np.hstack([_get_step_stp_idx_data(step_code, n=n) for _, step_code
            in step_order])


def _get_step_cyc_data(cyc, n=N_PER_STEP):
    """Returns step-type enum data for each datapoint of a single step.

    Parameters
    ----------
    cyc : int
        Cycle number of this step
    n : int
        Number of datapoints per step

    Returns
    -------
    step_cyc_data : np.array(int)
    """
    return cyc * np.ones(n)


def _get_cyc_data(step_order=STEP_ORDER, n=N_PER_STEP):
    """Returns np.array of cycle number data for sample data.

    Parameters
    ----------
    step_order : list of (int, char)
        List of (Cycle number, step type code) for steps in sample procedure.
    n : int
        Number of datapoints per step.

    Returns
    -------
    cyc_data : np.array(int)
    """
    return np.hstack([_get_step_cyc_data(cyc, n=n) for cyc, _ in step_order])


def _get_step_pot_data(step_code, n=N_PER_STEP, v_min=V_MIN, v_max=V_MAX):
    """Returns potential data for a single step.

    Parameters
    ----------
    step_code : char
        1 characater step code for this step
    n : int
        Number of datapoints per step
    v_min : float
        Minimum potential (i.e. after CC-discharge)
    v_max : float
        Maximum potential (i.e. after CC-charge)

    Returns
    -------
    step_pot_data : np.array(float)

    Raises
    ------
    DecoderRingError : when invalid `step_code` is encountered.
    """
    if step_code == 'C':
        return np.linspace(v_min, v_max, n, endpoint=True)
    elif step_code == 'RAC':
        return v_max * np.ones(n)
    elif step_code == 'D':
        return np.linspace(v_max, v_min, n, endpoint=True)
    elif step_code == 'RAD':
        return v_min * np.ones(n)
    else:
        raise DecoderRingError("Unknown step_code {}".format(step_code))


def _get_pot_data(step_order=STEP_ORDER, n=N_PER_STEP, v_min=V_MIN, v_max=V_MAX):
    """Returns np.array of potential data for sample data.

    Parameters
    ----------
    step_order : list of (int, char)
        List of (Cycle number, step type code) for steps in sample procedure.
    n : int
        Number of datapoints per step.
    v_min : float
        Minimum potential (i.e. after CC-discharge)
    v_max : float
        Maximum potential (i.e. after CC-charge)

    Returns
    -------
    pot_data : np.array(float)
    """
    return np.hstack([_get_step_pot_data(step_code, n=n, v_min=v_min,
            v_max=v_max) for _, step_code in step_order])


def _get_step_cur_data(step_code, n=N_PER_STEP, i_max=I_MAX):
    """Returns potential data for a single step.

    Parameters
    ----------
    step_code : char
        1 characater step code for this step
    n : int
        Number of datapoints per step
    i_max : float
        Constant current C/DC current

    Returns
    -------
    step_cur_data : np.array(float)

    Raises
    ------
    DecoderRingError : when invalid `step_code` is encountered.
    """
    if step_code == 'C':
        return i_max * np.ones(n)
    elif step_code == 'RAC':
        return np.zeros(n)
    elif step_code == 'D':
        return -1.0 * i_max * np.ones(n)
    elif step_code == 'RAD':
        return np.zeros(n)
    else:
        raise DecoderRingError("Unknown step_code {}".format(step_code))


def _get_cur_data(step_order=STEP_ORDER, n=N_PER_STEP, i_max=I_MAX):
    """Returns np.array of current data for sample data.

    Parameters
    ----------
    step_order : list of (int, char)
        List of (Cycle number, step type code) for steps in sample procedure.
    n : int
        Number of datapoints per step.
    i_max : float
        Constant current C/DC current

    Returns
    -------
    cur_data : np.array(float)
    """
    return np.hstack([_get_step_cur_data(step_code, n=n, i_max=i_max) for
            _,step_code in step_order])


def create_data(step_order=STEP_ORDER, n=N_PER_STEP, v_min=V_MIN, v_max=V_MAX,
        i_max=I_MAX):
    """Returns Dataframe of sample_data.

    Parameters
    ----------
    None

    Returns
    -------
    df : pd.DataFrame
        df of sample data.
    """

    # Set-up data frame
    df = pd.DataFrame(data={
        "dpt": np.hstack(_get_dpt_data(step_order=step_order, n=n)),
        "cyc": np.hstack(_get_cyc_data(step_order=step_order, n=n)),
        "stp": np.hstack(_get_stp_data(step_order=step_order, n=n)),
        "cur": np.hstack(_get_cur_data(step_order=step_order, n=n, i_max=i_max)),
        "pot": np.hstack(_get_pot_data(step_order=step_order, n=n, v_min=v_min,
                v_max=v_max)),
    })

    # Assume datapoint taken every half second
    df["time"] = df["dpt"] / 2.0

    # Populate the start-byte in every row (with the hex "AA").
    df["start"] = 170

    return df


def main():
    """Writes the sample data-set to file as a csv

    Returns path to where sample data file was saved.
    """
    filepath = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sample.csv"))
    df = create_data()

    df.to_csv(filepath, index=False)

    return filepath


if __name__ == "__main__":
    main()

