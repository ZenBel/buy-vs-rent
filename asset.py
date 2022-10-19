"""Basic asset class to escalate financial flows."""
import math
from typing import Callable
from typing import Dict
from typing import Optional

import numpy as np


def annual_to_monthly_return(annual_return: float) -> float:
    """Convert annual return to monthly.

    Parameters
    ----------
    annual_return: float
        annualized percentage return

    Returns
    -------
    float
        monthly percentage return
    """
    return (1 + annual_return) ** (1 / 12) - 1


def annual_to_monthly_stdev(annual_stdev: float) -> float:
    """Convert annual standard deviation to monthly. Careful with this one.

    It seems like a common method in financial modelling to just take the monthly
    standard deviation and multiply it by sqrt(12) to annualize it. So in reverse that
    would just be the formula below. I haven't looked into what assumptions have to
    hold for this to be valid and I'm planning to be a bit more careful with how I
    parameterise things. But as a first approximation it's a decent helper

    Parameters
    ----------
    annual_stdev: float
        annualized standard deviation

    Returns
    -------
    float
        monthly standard deviation
    """
    return annual_stdev / math.sqrt(12)


def distreturns(
    dist: Callable = np.random.normal,
    dist_args: Optional[Dict] = None,
    periods: int = 300,
    simulations: int = 100,
):
    """Simulate a series of returns from a given distribution.

    Lets you parameterize the distribution it's drawn from,
    Specify the number of simulations and periods to simulate for,
    and plot results of the simulations

    Notes
    -----
    Right now this does not assume any tax on capital gains on the portfolio. You can
    hack around that by inputing a tax adjusted expected return.

    Parameters
    ----------
    dist: Callable, default np.random.normal
        The distribution from which returns are drawn
    dist_args : dict
        dictionary of kwargs to be passed along with dist defaults to
        mean 0.006, standard deviation 0.06
    periods: int, default 300
        Number of periods to simulate
    simulations: int, default 100
        Number of simulations to run

    Returns
    -------
    np.ndarray
        periods x simulations array of cumulative returns for the asset
        I think of it as the price of a security (with no dividends etc)
        normalized to = 1 in the first period. You can then take a series of
        cash flows to compute the number of shares in that asset you can buy
        in a given period, cumulatively sum those shares, and then multiply them by
        the asset price for any period to determine total wealth accumulated
    """
    if dist_args is None:
        dist_args = {"loc": 0.006, "scale": 0.06}
    returns = (1 + dist(**dist_args, size=(periods, simulations))).cumprod(
        axis=0
    )
    returns[0] = 1
    return returns


def inflated_series(amount, inflation, simulation_periods):
    """Project an initial value over the forecast period with inflation.

    Parameters
    ----------
    amount: numeric
        The value to inflate

    Returns
    -------
    array_like
        The value projected into the future
    """
    base_inflate = np.full(simulation_periods, 1 + inflation).cumprod()
    inflated = base_inflate * amount
    return inflated
