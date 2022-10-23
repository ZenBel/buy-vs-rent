from flask import Flask, jsonify, request
import numpy as np
from rentorbuy import RentOrBuy
from asset import annual_to_monthly_stdev, annual_to_monthly_return


def data_check(data):
    ## TODO: Data checks
    return data


app = Flask(__name__)


@app.post("/mortgage_payments")
def calculate_mortgage_payments():
    data = request.json

    data = data_check(data)

    mgt = RentOrBuy(
        monthly_rent=data["monthly_rent"],
        house_price=data["house_price"],
        woz_value=data["woz_value"],
        eigenwoningforfait=data["eigenwoningforfait"],
        down_payment=data["down_payment"],
        mortgage_amortization_years=data["loan_term"],
        mortgage_apr=data["interest_rate"],
        additional_purchase_costs=data["purchase_costs"],
        additional_monthly_costs=data["monthly_costs"],
        mortgage_additional_payments=data["extra_repayment_amount"],
        annual_inflation=data["inflation"],
        monthly_property_tax_rate=data["property_tax"],
        maintenance_cost=data["maintenance_cost"],
        housing_asset_dict={
            "dist": np.random.normal,
            "dist_args": {
                "loc": annual_to_monthly_return(0.0735),
                "scale": annual_to_monthly_stdev(0.0860),
            },
        },
        investment_asset_dict={
            "dist": np.random.normal,
            "dist_args": {
                "loc": annual_to_monthly_return(0.1195),
                "scale": annual_to_monthly_stdev(0.198),
            },
        },
        number_of_simulations=10000,
    )

    return jsonify(mgt.mortgage_df.reset_index(drop=True).to_dict())


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
