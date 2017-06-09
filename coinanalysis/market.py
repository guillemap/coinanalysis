#!/usr/bin/env python
import sys
import os.path
sys.path.append(os.path.dirname(__file__) + "/../python-bittrex/bittrex")
from bittrex import Bittrex, BUY_ORDERBOOK, SELL_ORDERBOOK, BOTH_ORDERBOOK
import pandas as pd


class Market(object):
    """
    Used to provide analysis of a market on Bittrex.
    """

    def __init__(self, name, bittrex=None):
        """
        :param name: String literal for the market (e.g. BTC-LTC)
        :type name: str
        :param bittrex: Instance of Bittrex, potentially with API_KEY and SECRET
        :type bittrex: Bittrex
        """
        self.name = name
        self.basis, self.coin = self.name.split("-")
        if bittrex:
            self.bittrex = bittrex
        else:
            self.bittrex = Bittrex(None, None)

    @property
    def summary(self):
        response = self.bittrex.get_market_summary(self.name)
        if response['success']:
            return response['result'][0]
        raise Exception(
            "Could not retrieve data from Bittrex: {:s}".format(response['message'])
        )

    @property
    def history(self):
        response = self.bittrex.get_market_history(self.name)
        if response['success']:
            df = pd.DataFrame(response['result'])
            df["TimeStamp"] = pd.to_datetime(df["TimeStamp"])
            return df
        raise Exception(
            "Could not retrieve data from Bittrex: {:s}".format(response['message'])
        )

    def _get_orderbook(self, depth_type, depth=20):
        response = self.bittrex.get_orderbook(self.name, depth_type, depth)
        if response['success']:
            return pd.DataFrame(response['result'])
        raise Exception(
            "Could not retrieve data from Bittrex: {:s}".format(response['message'])
        )

    def get_buy_orderbook(self, depth=20):
        return self._get_orderbook(BUY_ORDERBOOK, depth)

    def get_sell_orderbook(self, depth=20):
        return self._get_orderbook(SELL_ORDERBOOK, depth)


    def get_both_orderbooks(self, depth=20):
        response = self.bittrex.get_orderbook(self.name, BOTH_ORDERBOOK, depth)
        if response['success']:
            return (
                pd.DataFrame(response['result']['buy']),
                pd.DataFrame(response['result']['sell'])
            )
        raise Exception(
            "Could not retrieve data from Bittrex: {:s}".format(response['message'])
        )

    @property
    def ticker(self):
        response = self.bittrex.get_ticker(self.name)
        if response['success']:
            return response['result']
        raise Exception(
            "Could not retrieve data from Bittrex: {:s}".format(response['message'])
        )

    def get_price_time_series(self):
        return self.history[["TimeStamp", "Price"]]

    def __str__(self):
        return "{:s}\t{:s}".format(self.name, str(self.ticker))
