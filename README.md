# buy-vs-rent
Find out whether it is more convenient to buy or rent a house in your city.

The basic calculation is inspired by Ben Felix's video "[Renting vs. Buying a Home: The 5% Rule](https://www.youtube.com/watch?v=Uwl3-jBNEd4&t=380s)" but allows more flexibility in specifying the unrecoverable costs of owning. 

When deciding whether buying a house is a good financial decision, one should compare the total unrecoverable costs of renting to the total unrecoverable costs of buying. "Unrecoverable costs" comprehend all that money you throw down the toilet when choosing either option.

Total monthly unrecoverable costs of renting:
- Rent
- (Other smaller costs)

Total monthly unrecoverable costs of buying:
- Property taxes
- Maintenance costs
- Cost of equity capital (i.e. the cost of investing in real estate vs. investing in, say, a low-cost index fund like the S&P500. These costs can be positive when the index fund is expected to have higher returns than real estate over the mortgage term, or viceversa).
- Cost of debt capital (i.e. the interest you pay on your mortgage)

Can you find a rental apartment similar to the one you want to buy for which `Total monthly unrecoverable costs of renting < Total monthly unrecoverable costs of buying`?

If yes, then renting is a better financial decision than buying.

Assumptions and approximations
- In NL, property tax should be a function of the catastal value of the house and not of the purchase value.
- Only annuity mortgages with fixed interest rate are considered
- No closing costs when selling the house are considered
- Property taxes, maintenance costs, and additional monthly costs of the house are assumed to increase by the same percentage as the inflation rate.
- Rent is assumed to increase by the same percentage as the inflation rate.