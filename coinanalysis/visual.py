#!/usr/bin/env python

import matplotlib.pyplot as plt


def view_price_time_series(market):
    market.history.plot(x="TimeStamp", y="Price")
    plt.title(market.name)
    plt.xlabel("Time")
    plt.ylabel("Price [{:s}]".format(market.basis))
    plt.show()