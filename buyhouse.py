import numpy_financial as npf
import numpy as np


class BuyHouse:
    def __init__(
        self,
        market_price: float,
        mortgage_downpayment: float,
        mortgage_interests: float,
        mortgage_term: float,
        sqm: float,
        maintenance_cost: float = None,
        property_tax: float = None,
        return_sp: float = None,
        return_ret: float = None,
    ) -> None:

        self.market_price = market_price
        self.mdp = mortgage_downpayment
        self.mint = mortgage_interests / 100
        self.mterm = mortgage_term
        self.sqm = sqm
        if maintenance_cost is not None:
            self.maint_cost = maintenance_cost
        else:
            # Assumed to be 25.00 euro/sqm per year
            # source: https://drive.google.com/file/d/1sqQmFAEhn3zZMrVzSH8SAuIN2u80rjcq/view
            self.maint_cost = 25.00  # euros/sqm per year
        if property_tax is not None:
            self.property_tax = property_tax / 100
        else:
            # For Amsterdam OZB is 0.0420% of WOZ waarde
            # WOZ waarde is usually less than house market price
            # so we round OZB down to 0.04 %
            self.property_tax = 0.04 / 100
        if return_sp is not None:
            self.return_sp = return_sp / 100
        else:
            # Forecasted avg return of sp500 over the loan term.
            # Value based on historical average over the last 50 year.
            # Source: https://www.fool.com/investing/how-to-invest/stocks/average-stock-market-return/
            self.return_sp = 9 / 100
        if return_ret is not None:
            self.return_ret = return_ret / 100
        else:
            # Forecasted avg return of real estate in the
            # city/neighborhood where you are buying over the loan term.
            # Value based on historical average for NL real estate market.
            # Source: https://www.ceicdata.com/en/indicator/netherlands/house-prices-growth
            self.return_ret = 5 / 100

    def get_overview(self, how="annual"):
        print(
            f"Avg. annual property tax cost: {self.compute_property_tax():.2f}."
        )
        print(
            f"Avg. annual maintenance cost: {self.compute_maintenance_cost():.2f}."
        )
        print(
            f"Avg. annual cost of equity capital: {self.compute_cost_of_equity_capital():.2f}."
        )
        print(
            f"Avg. annual cost of debt capital: {self.compute_cost_of_debt_capital():.2f}."
        )
        print()
        if how == "annual":
            print(
                f"Total annual unrecoverable costs: {self.unrecoverable_costs():.2f}."
            )
        if how == "monthly":
            print(
                f"Total monthly unrecoverable costs: {self.unrecoverable_costs('monthly'):.2f}."
            )
        print()
        print(
            f"For you the {self.unrecoverable_costs()/self.market_price*100:.2f}% rule holds!"
        )

    def unrecoverable_costs(self, how="annual"):
        """Annual unrecoverable costs of renting."""
        self.property_tax_cost = self.compute_property_tax()
        self.maintenance_cost = self.compute_maintenance_cost()
        self.cost_of_equity_capital = self.compute_cost_of_equity_capital()
        self.cost_of_debt_capital = self.compute_cost_of_debt_capital()

        self.yearly_unrecoverable_costs = (
            self.property_tax_cost
            + self.maintenance_cost
            + self.cost_of_equity_capital
            + self.cost_of_debt_capital
        )

        if how == "annual":
            return self.yearly_unrecoverable_costs
        elif how == "monthly":
            return self.yearly_unrecoverable_costs / 12

    def compute_property_tax(self):
        """Annual property tax."""
        return self.property_tax * self.market_price

    def compute_maintenance_cost(self):
        """Annual maintenance cost."""
        return self.maint_cost * self.sqm

    def compute_cost_of_equity_capital(self):
        """Annual cost of equity, i.e. the cost of having money
        invested in real estate instead of in the sp500 (can be
        +ve and -ve depending on the expected avg. return of the
        two investments over the loan term."""
        # TODO: Add extra returns due to principal repayment, i.e.
        # when repaying the mortgage principal you are investing money in real estate
        # that could otherwise be invested in the sp500. This should be added
        # to the cost of equity capital.
        return (self.return_sp - self.return_ret) * self.mdp

    def compute_cost_of_debt_capital(self):
        """Annual cost of having a debt, i.e. the avg. yearly interests
        you pay for your loan/mortgage."""
        # Total cost of having a loan over the whole loan term
        total_cost_of_debt_capital = abs(
            sum(
                npf.ipmt(
                    self.mint / 12,  # monthly interest rate
                    np.arange(self.mterm * 12) + 1,  # number of repayments
                    self.mterm * 12,  # loan term in months
                    self.market_price - self.mdp,  # loan principal
                )
            )
        )
        # Avg yearly cost of having a loan
        return total_cost_of_debt_capital / self.mterm
