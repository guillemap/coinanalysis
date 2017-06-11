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
        self.bittrex = bittrex if bittrex else Bittrex(None, None)
        self.update()

    def update(self, lazy=True):
        """
        Set all the data fields of the Market to None.  They are lazily populated when
        called for if lazy is True.
        :param lazy: if lazy, Market data are lazily populated upon calling them.
        :return:
        """
        if lazy:
            self._summary = None
            self._history = None
            self._ticker = None
            self._buy_orderbook = None
            self._sell_orderbook = None
            self._both_orderbooks = None
            return 0
        self.summary
        self.history
        self.ticker
        self.get_buy_orderbook()
        self.get_sell_orderbook()
        self.get_both_orderbooks()

    @property
    def summary(self):
        if not self._summary:
            response = self.bittrex.get_market_summary(self.name)
            if response['success']:
                self._summary = response['result'][0]
                return self._summary
            raise Exception(
                "Could not retrieve data from Bittrex: {:s}".format(response['message'])
            )
        return self._summary

    @property
    def history(self):
        """
        Columns of the returned DataFrame are:
        "FillType", "Id", "OrderType", "Price", "Quantity", "TimeStamp" and "Total"
        """
        if not self._history:
            response = self.bittrex.get_market_history(self.name)
            if response['success']:
                self._history = pd.DataFrame(response['result'])
                self._history["TimeStamp"] = pd.to_datetime(self._history["TimeStamp"])
                return self._history
            raise Exception(
                "Could not retrieve data from Bittrex: {:s}".format(response['message'])
            )
        return self._history

    @property
    def ticker(self):
        """
        Returns a dictionary of prices with keys "Last", "Bid" and "Ask".
        :return: dict
        """
        if not self._ticker:
            response = self.bittrex.get_ticker(self.name)
            if response['success']:
                self._ticker = response['result']
                return self._ticker
            raise Exception(
                "Could not retrieve data from Bittrex: {:s}".format(response['message'])
            )
        return self._ticker

    def _get_orderbook(self, depth_type, depth=20):
        response = self.bittrex.get_orderbook(self.name, depth_type, depth)
        if response['success']:
            return pd.DataFrame(response['result'])
        raise Exception(
            "Could not retrieve data from Bittrex: {:s}".format(response['message'])
        )

    def get_buy_orderbook(self, depth=20):
        if not self._buy_orderbook:
            self._buy_orderbook = self._get_orderbook(BUY_ORDERBOOK, depth)
        return self._buy_orderbook

    def get_sell_orderbook(self, depth=20):
        if not self._sell_orderbook:
            self._sell_orderbook = self._get_orderbook(SELL_ORDERBOOK, depth)
        return self._sell_orderbook

    def get_both_orderbooks(self, depth=20):
        if not self._both_orderbooks:
            response = self.bittrex.get_orderbook(self.name, BOTH_ORDERBOOK, depth)
            if response['success']:
                self._both_orderbooks = {
                    "buy": pd.DataFrame(response['result']['buy']),
                    "sell": pd.DataFrame(response['result']['sell'])
                }
                return self._both_orderbooks
            raise Exception(
                "Could not retrieve data from Bittrex: {:s}".format(response['message'])
            )
        return self._both_orderbooks

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
