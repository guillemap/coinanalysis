#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os.path
sys.path.append(os.path.dirname(__file__) + "/../python-bittrex/bittrex")
from bittrex import Bittrex, BUY_ORDERBOOK, SELL_ORDERBOOK, BOTH_ORDERBOOK
import pandas as pd
from datetime import datetime

LEDGER_TIME_FORMAT = "%Y/%m/%d %H:%M:%S"

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
        self.basis, self.code = self.name.split("-")
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
        """
        Columns of the returned DataFrame are:
        "FillType", "Id", "OrderType", "Price", "Quantity", "TimeStamp" and "Total"
        """
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
            return {
                "buy": pd.DataFrame(response['result']['buy']),
                "sell": pd.DataFrame(response['result']['sell'])
            }
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

    def get_ledger_cli_entry(self):
        """
        Get a string that can be entered into a pricedb for ledger CLI
        :return: str
        """
        if self.basis in ("$", "¥", "£"):
            #TODO make this more robust
            return "P {:s} {:s} {:s}{:.2f}".format(
                    datetime.now().strftime(LEDGER_TIME_FORMAT),
                    self.code,
                    self.basis,
                    self.ticker["Last"]
                    )
        return "P {:s} {:s} {:f} {:s}".format(
                datetime.now().strftime(LEDGER_TIME_FORMAT),
                self.code,
                self.ticker["Last"],
                self.basis
                )


    def __str__(self):
        return "{:s}\t{:s}".format(self.name, str(self.ticker))
