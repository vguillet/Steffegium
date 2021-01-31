
##################################################################################################################
"""
This script contains the Prototype_5 class
This prototype is based entirely on technical analysis, and include new indicators, including:
    - EMA
    - LWMA

The following parameter_set still require manual input:
    - spline interpolation coef
    - include trigger in signals (Technical_Indicators output generation)
    - buffer and buffer settings (Threshold determination)

TO DO: Auto max/min parameter indicator normalisation (in indicator script)?
"""

# Libs
import numpy as np

# Own modules
from PhyTrade.Economic_model.Building_blocks.Big_Data import BIGDATA
# ---> Import model settings
from PhyTrade.Settings.Class_based_settings.Model_settings import Model_settings

# ---> Import indicators
from PhyTrade.Economic_model.Building_blocks.Technical_indicators.Technical_Indicators.RSI import RSI
from PhyTrade.Economic_model.Building_blocks.Technical_indicators.Technical_Indicators.SMA import SMA
from PhyTrade.Economic_model.Building_blocks.Technical_indicators.Technical_Indicators.EMA import EMA
from PhyTrade.Economic_model.Building_blocks.Technical_indicators.Technical_Indicators.LWMA import LWMA
from PhyTrade.Economic_model.Building_blocks.Technical_indicators.Technical_Indicators.CCI import CCI
from PhyTrade.Economic_model.Building_blocks.Technical_indicators.Technical_Indicators.EOM import EOM
from PhyTrade.Economic_model.Building_blocks.Technical_indicators.Technical_Indicators.OC_avg_gradient import OC_avg_gradient

# ---> Import amplification signals
from PhyTrade.Economic_model.Building_blocks.Technical_indicators.Amplification_signals.Volume import Volume
from PhyTrade.Economic_model.Building_blocks.Technical_indicators.Amplification_signals.Volatility import Volatility

# ---> import general tools
from PhyTrade.Economic_model.Tools.OC_tools import OC
from PhyTrade.Tools.Math_tools import Math_tools
from PhyTrade.Tools.Spline_tools import Spline_tools

__version__ = '1.1.1'
__author__ = 'Victor Guillet'
__date__ = '12/14/2018'

##################################################################################################################


class Prototype_5:
    def __init__(self, parameter_dictionary, data_slice):
        """
        Generate a model containing all coded indicators, process and generate bullish/bearish signals

        :param parameter_dictionary: Dictionary of dictionaries containing the values for all the variables of each signal
        :param data_slice: data_slice class instance
        """

        # ========================= ANALYSIS INITIALISATION ==============================
        # --> Fetch model settings
        settings = Model_settings()
        settings.gen_model_settings()

        # --> Initiate records
        self.big_data = BIGDATA(data_slice, parameter_dictionary)

        # ~~~~~~~~~~~~~~~~~~ Building_blocks initialisation
        self.oc_tools = OC()
        self.spline_tools = Spline_tools(self.big_data)
        self.math_tools = Math_tools()

        # ~~~~~~~~~~~~~~~~~~ Technical_Indicators initialisation
        # --> RSI initialisation
        self.big_data.content["indicators"]["rsi"] = []

        for i in range(parameter_dictionary["indicators_count"]["rsi"]):
            self.big_data.content["indicators"]["rsi"].append(
                RSI(big_data=self.big_data,
                    timeframe=parameter_dictionary["indicator_properties"]["timeframes"]["rsi_"+str(i)],
                    standard_upper_threshold=parameter_dictionary["indicator_properties"]["rsi_standard_upper_thresholds"]["rsi_" + str(i)],
                    standard_lower_threshold=parameter_dictionary["indicator_properties"]["rsi_standard_lower_thresholds"]["rsi_" + str(i)],
                    buffer_setting=parameter_dictionary["general_settings"]["rsi_buffer_setting"]))

        # --> SMA initialisation
        self.big_data.content["indicators"]["sma"] = []

        for i in range(parameter_dictionary["indicators_count"]["sma"]):
            self.big_data.content["indicators"]["sma"].append(
                SMA(big_data=self.big_data,
                    timeperiod_1=parameter_dictionary["indicator_properties"]["timeframes"]["sma_"+str(i)+"_1"],
                    timeperiod_2=parameter_dictionary["indicator_properties"]["timeframes"]["sma_"+str(i)+"_2"]))

        # --> EMA initialisation
        self.big_data.content["indicators"]["ema"] = []

        for i in range(parameter_dictionary["indicators_count"]["ema"]):
            self.big_data.content["indicators"]["ema"].append(
                EMA(big_data=self.big_data,
                    timeperiod_1=parameter_dictionary["indicator_properties"]["timeframes"]["ema_"+str(i)+"_1"],
                    timeperiod_2=parameter_dictionary["indicator_properties"]["timeframes"]["ema_"+str(i)+"_2"]))

        # --> LWMA initialisation
        self.big_data.content["indicators"]["lwma"] = []

        for i in range(parameter_dictionary["indicators_count"]["lwma"]):
            self.big_data.content["indicators"]["lwma"].append(
                LWMA(big_data=self.big_data,
                     timeperiod=parameter_dictionary["indicator_properties"]["timeframes"]["lwma_"+str(i)]))

        # --> CCI initialisation
        self.big_data.content["indicators"]["cci"] = []

        for i in range(parameter_dictionary["indicators_count"]["cci"]):
            self.big_data.content["indicators"]["cci"].append(
                CCI(big_data=self.big_data,
                    timeperiod=parameter_dictionary["indicator_properties"]["timeframes"]["cci_"+str(i)]))

        # --> EOM initialisation
        self.big_data.content["indicators"]["eom"] = []

        for i in range(parameter_dictionary["indicators_count"]["eom"]):
            self.big_data.content["indicators"]["eom"].append(
                EOM(big_data=self.big_data,
                    timeperiod=parameter_dictionary["indicator_properties"]["timeframes"]["eom_"+str(i)]))

        # --> OC_avg_gradient initialisation
        self.big_data.content["indicators"]["oc_gradient"] = []

        for i in range(parameter_dictionary["indicators_count"]["oc_gradient"]):
            self.big_data.content["indicators"]["oc_gradient"].append(
                OC_avg_gradient(big_data=self.big_data))

        # ~~~~~~~~~~~~~~~~~~ Amplification signal initialisation
        # --> Volume initialisation
        self.big_data.volume = Volume(big_data=self.big_data,
                                      amplification_factor=parameter_dictionary["spline_property"]["amplification_factor"]["volume_0"])

        # --> Volatility initialisation
        self.big_data.volatility = Volatility(big_data=self.big_data,
                                              timeframe=parameter_dictionary["indicator_properties"]["timeframes"]["volatility_0"],
                                              amplification_factor=parameter_dictionary["spline_property"]["amplification_factor"]["volatility_0"])

        # ================================================================================
        """




        """
        # ========================= DATA GENERATION AND PROCESSING =======================
        # ~~~~~~~~~~~~~~~~~~ Technical_Indicators output generation
        # --> Generate output of every indicator
        for indicator_type in parameter_dictionary["indicators_count"]:
            if parameter_dictionary["indicators_count"][indicator_type] != 0:
                for indicator in self.big_data.content["indicators"][indicator_type]:
                    indicator.get_output(big_data=self.big_data,
                                         include_triggers_in_bb_signal=parameter_dictionary["general_settings"]["include_triggers_in_bb_signal"][indicator_type])

        # --> Creating splines from indicator signals
        for indicator_type in parameter_dictionary["indicators_count"]:
            if parameter_dictionary["indicators_count"][indicator_type] != 0:
                self.big_data.content["indicator_splines"][indicator_type] = []
                for i in range(len(self.big_data.content["indicators"][indicator_type])):
                    self.big_data.content["indicator_splines"][indicator_type].append(
                        self.spline_tools.calc_signal_to_spline(big_data=self.big_data,
                                                                signal=self.big_data.content["indicators"][indicator_type][i].bb_signal,
                                                                smoothing_factor=parameter_dictionary["spline_property"]["smoothing_factors"][indicator_type + "_" + str(i)]))

        # ~~~~~~~~~~~~~~~~~~ BB signals processing
        # --> Generating amplification signals
        self.big_data.spline_volume = \
            self.spline_tools.calc_signal_to_spline(big_data=self.big_data,
                                                    signal=self.big_data.volume.amp_coef,
                                                    smoothing_factor=parameter_dictionary["spline_property"]["smoothing_factors"]["volume_0"])

        self.big_data.spline_volatility = \
            self.spline_tools.calc_signal_to_spline(big_data=self.big_data,
                                                    signal=self.big_data.volatility.amp_coef,
                                                    smoothing_factor=parameter_dictionary["spline_property"]["smoothing_factors"]["volatility_0"])

        # --> Tuning separate signals
        for indicator_type in parameter_dictionary["indicators_count"]:
            if parameter_dictionary["indicators_count"][indicator_type] != 0:
                for i in range(len(self.big_data.content["indicator_splines"][indicator_type])):
                    if parameter_dictionary["spline_property"]["flip"][indicator_type+"_"+str(i)] is True:
                        self.big_data.content["indicator_splines"][indicator_type][i] = \
                            self.spline_tools.flip_spline(spline=self.big_data.content["indicator_splines"][indicator_type][i])

        # --> Adding signals together
        # Creating signal array
        self.big_data.spline_array = np.zeros(shape=(sum(parameter_dictionary["indicators_count"].values()), data_slice.subslice_size*self.big_data.spline_multiplication_coef))
        self.big_data.weights_array = np.zeros(shape=(sum(parameter_dictionary["indicators_count"].values()), 1))

        counter = 0
        for indicator_type in self.big_data.content["indicator_splines"]:
            for i in range(len(self.big_data.content["indicator_splines"][indicator_type])):
                self.big_data.spline_array[counter] = self.big_data.content["indicator_splines"][indicator_type][i]
                self.big_data.weights_array[counter] = parameter_dictionary["spline_property"]["weights"][indicator_type+"_"+str(i)]
                counter += 1

        self.big_data.major_spline = self.spline_tools.combine_splines(spline_array=self.big_data.spline_array,
                                                                       weights_array=self.big_data.weights_array)

        # ---- Tuning combined signal
        # self.big_data.major_spline = \
        #     self.spline_tools.modulate_amplitude_spline(self.big_data.major_spline,
        #                                                 self.big_data.spline_volume,
        #                                                 std_dev_max=settings.volume_std_dev_max)
        #
        # self.big_data.major_spline = \
        #     self.spline_tools.modulate_amplitude_spline(self.big_data.major_spline,
        #                                                 self.big_data.spline_volatility,
        #                                                 std_dev_max=settings.volatility_std_dev_max)

        # ---- Normalise major_spline between -1 and 1
        self.big_data.major_spline = self.math_tools.normalise_minus_one_one(self.big_data.major_spline)
        # self.big_data.major_spline = self.math_tools.alignator_minus_one_one(self.big_data.major_spline,
        #                                                                      25,
        #                                                                      -25)

        # ~~~~~~~~~~~~~~~~~~ Threshold determination
        # ---- Creating dynamic thresholds
        upper_threshold, lower_threshold = \
            self.spline_tools.calc_thresholds(big_data=self.big_data,
                                              spline=self.big_data.major_spline,
                                              buffer=settings.buffer,
                                              standard_upper_threshold=parameter_dictionary["spline_property"]["major_spline_standard_upper_thresholds"],
                                              standard_lower_threshold=parameter_dictionary["spline_property"]["major_spline_standard_lower_thresholds"],
                                              bband_timeframe=parameter_dictionary["indicator_properties"]["timeframes"]["threshold_timeframe"],
                                              threshold_setting=parameter_dictionary["general_settings"]["threshold_setting"],
                                              buffer_setting=parameter_dictionary["general_settings"]["buffer_setting"])

        # ~~~~~~~~~~~~~~~~~~ Creating Major Spline_tools/trigger values and trading indicators splines
        # --> Generating Major spline
        self.big_data.gen_major_and_trade_results(upper_threshold=upper_threshold,
                                                  lower_threshold=lower_threshold)

        # --> Generating trading indicators
        for indicator_type in parameter_dictionary["indicators_count"]:
            if parameter_dictionary["indicators_count"][indicator_type] != 0:
                self.big_data.content["trading_indicator_splines"][indicator_type] = []
                for i in range(len(self.big_data.content["indicators"][indicator_type])):
                    self.big_data.content["trading_indicator_splines"][indicator_type].append(
                        self.spline_tools.calc_trading_indicator(big_data=self.big_data,
                                                                 spline=self.big_data.content["indicator_splines"][indicator_type][i]))
