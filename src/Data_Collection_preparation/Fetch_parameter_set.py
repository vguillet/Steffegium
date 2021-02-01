
##################################################################################################################
"""
Used to fetch parameter sets
"""

# Libs
import json
import os

__version__ = '1.1.1'
__author__ = 'Victor Guillet'
__date__ = '10/09/2019'

##################################################################################################################


def fetch_parameter_set(ticker, run_count, term="Short_term"):

    path = r"Data\EVOA_results\Parameter_sets\%%\Run_##_**.json"
    path = path.replace('\\', '/').replace('##', str(run_count)).replace('**', ticker).replace('%%', term)

    # ---> Check if generated path data exists in database
    if os.path.exists(path):
        return json.load(open(path))
    else:
        print("Run_"+str(run_count)+"_"+ticker, "parameter set does not exist")
        return None


def fetch_parameter_sets(tickers, run_count, term="Short_term"):
    parameter_sets = []
    traded_tickers = []
    for ticker in tickers:
        param_set = fetch_parameter_set(ticker, run_count, term)
        if param_set is not None:
            traded_tickers.append(ticker)
            parameter_sets.append(param_set)

    assert(len(traded_tickers) == len(parameter_sets))
    return traded_tickers, parameter_sets