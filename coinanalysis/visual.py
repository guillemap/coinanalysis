#!/usr/bin/env python

import matplotlib.pyplot as plt


def view_price_time_series(market, rolling_mean_window=3):
    history = market.history
    history = history.assign(
        PriceRollingMean=history["Price"].rolling(window=rolling_mean_window, center=False).mean()
    )
    history.plot(x="TimeStamp", y=["PriceRollingMean","Price"])
    plt.title(market.name)
    plt.xlabel("Time")
    plt.ylabel("Price [{:s}]".format(market.basis))
    plt.show()