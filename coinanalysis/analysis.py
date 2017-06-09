#!/usr/bin/env python
import sys
import os.path
sys.path.append(os.path.dirname(__file__) + "/../python-bittrex/bittrex")
from bittrex import Bittrex
from market import Market


def get_highest_volume_markets(number=5, base=False):
    """
    Used to obtain the highest volume markets on Bittrex, sorted from highest volume to lowest volume
    :param number: How many markets you want
    :type number: int
    :param base: If true, return the highest base volume markets rather than just the highest
    :            volume markets
    :type base: bool
    :return: list of Market objects
    """
    b = Bittrex(None, None)
    response = b.get_market_summaries()
    if response['success']:
        volumes_markets = []
        for summary in response['result']:
            volumes_markets.append(
                    (summary["BaseVolume"] if base else summary['Volume'],
                    summary['MarketName'])
                    )
        volumes_markets.sort(reverse=True)
        markets = []
        for volume_market in volumes_markets[:number]:
            volume, market = volume_market
            markets.append(Market(market))
        return markets
    else:
        raise Exception(response['message'])


def get_inactive_markets():
    """
    Used to obtain the set of markets that are not currently active on Bittrex
    :return: list of Market objects
    """
    b = Bittrex(None, None)
    response = b.get_markets()
    if response['success']:
        markets = response['result']
        inactive_markets = []
        for market in markets:
            if not market['IsActive']:
                inactive_markets.append(Market(market['MarketName']))
                print "{:s}\t{:s}".format(market['MarketName'], market['Notice'])
        return inactive_markets
    else:
        raise Exception(response['message'])


def get_active_markets():
    """
    Used to obtain the set of markets that are currently active on Bittrex
    :return: list of Market objects
    """
    b = Bittrex(None, None)
    response = b.get_markets()
    if response['success']:
        markets = response['result']
        active_markets = []
        for market in markets:
            if market['IsActive']:
                active_markets.append(Market(market['MarketName']))
        return active_markets
    else:
        raise Exception(response['message'])
