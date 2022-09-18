"""Logic related to houses."""
import math
from collections import OrderedDict
from datetime import date

import numpy_financial as npf
import pandas as pd
from dateutil.relativedelta import relativedelta


class House:
    """House object, you buy one of these.

    Parameters
    ----------
    value: numeric
        The purchase price of the house (including overbid)
    """

    def __init__(self, value):
        self.value = value

    def monthly_property_tax(self, rate: float = 0.00042):
        """Calculate monthly property tax.

        Based off Amsterdam OZB tax for year 2022.
        Source: https://www.amsterdam.nl/en/municipal-taxes/property-tax-ozb/

        Parameters
        ----------
        rate: float, default 0.00042
            annual tax rate

        Returns
        -------
        float
            The monthly property tax on the house.
        """
        return self.value * rate / 12

    def buy(self, down_payment, additional_costs=None):
        """Buy the house.

        Parameters
        ----------
        down_payment: numeric
            The euro amount of the down payment
        additional_costs: numeric, default to 5% of the cost
            of the house. They include legal fees, title insurance,
            home inspection, home appraisal, etc.

        Returns
        -------
        dict
            {'mortgage': mortgage_amt, 'cash': cash}:
            dictionary returning numeric values for amount
            to be mortgaged and cash up front required for purchase
        """
        mortgage_amt = self.value - down_payment
        if additional_costs is None:
            additional_costs = 0.05 * self.value
        cash = down_payment + additional_costs
        return {"mortgage": mortgage_amt, "cash": cash}

    def sell(self):
        """Sell the house.

        Eventually we'll want to add closing costs and other
        things in here, but for now this just returns the value

        Returns
        -------
        self.value: numeric
            Just the value of the house
        """
        return self.value


class Mortgage:
    """Base mortgage class.

    Parameters
    ----------
    principal: numeric
        Value of the mortgage
    years: int
        Amortization period of the mortgage (not term of fixed rate)
    rate: float
        mortgage annual interest rate (including fees), i.e. APR rate.
    """

    def __init__(self, principal, years, rate):
        self.principal = principal
        self.years = years
        self.rate = rate

    def monthly_payment(self):
        """Calculate payments required for a monthly payment schedule.

        Takes APR as an input and compounds semi annually for AER. Canadian
        mortgages are dumb like that.

        Returns
        -------
        pmt: float
            The amount of the monthly payment
        """
        rate = self.rate
        # monthly interest rate
        periodic_interest_rate = (1 + rate) ** (1 / 12) - 1
        # monthly repayment period
        periods = self.years * 12
        pmt = -round(
            npf.pmt(periodic_interest_rate, periods, self.principal), 2
        )
        return pmt

    def amortize(self, addl_pmt=0):
        """Show payments on the mortgage.

        Parameters
        ----------
        addl_pmt: numeric, default 0
            additional regular contributions
        payment_type: ["monthly", "bi_weekly", "acc_bi_weekly"], default "monthly"
            type of payment plan

        Returns
        -------
        df: pandas.DataFrame
            Dataframe of mortgage payments showing principal and interest contributions
            and amount outstanding
        """

        def amortizdict(adp=addl_pmt):
            """Yield a dictionary to convert to dataframe.

            Parameters
            ----------
            adp: float
                Additional payment to be made beyond the requirement

            Yields
            ------
            Dict
                All the data for another period of mortgage payments
            """
            pmt = self.monthly_payment()
            rate = (1 + (self.rate / 2)) ** 2 - 1
            periodic_interest_rate = (1 + rate) ** (1 / 12) - 1
            date_increment = relativedelta(months=1)

            # initialize the variables to keep track of the periods and running balance
            per = 1
            beg_balance = self.principal
            end_balance = self.principal
            start_date = date.today().replace(day=1) + relativedelta(months=1)

            while end_balance > 0:
                # recalculate interest based on the current balance
                interest = round(periodic_interest_rate * beg_balance, 2)

                # Determine payment based on whether this will pay off the loan
                pmt = min(pmt, beg_balance + interest)
                principal = pmt - interest

                # Ensure additional payment gets adjusted if the loan is being paid off
                adp = min(adp, beg_balance - principal)
                end_balance = beg_balance - (principal + adp)

                yield OrderedDict(
                    [
                        ("Date", start_date),
                        ("Period", per),
                        ("Begin_balance", beg_balance),
                        ("Payment", pmt),
                        ("Principal", principal),
                        ("Interest", interest),
                        ("Additional_payment", adp),
                        ("End_balance", end_balance),
                    ]
                )
                # increment the counter, balance and date
                per += 1
                start_date += date_increment
                beg_balance = end_balance

        df = (
            pd.DataFrame(amortizdict())
            .assign(Date=lambda df: pd.to_datetime(df["Date"]))
            .set_index("Date")
            .drop(columns=["Period"])
            .resample("MS")
            .agg(
                {
                    "Begin_balance": "max",
                    "Payment": "sum",
                    "Principal": "sum",
                    "Interest": "sum",
                    "Additional_payment": "sum",
                    "End_balance": "min",
                }
            )
            .assign(
                total_payment=lambda df: df["Payment"]
                + df["Additional_payment"]
            )
        )
        return df
