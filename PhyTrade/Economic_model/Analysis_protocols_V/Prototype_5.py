"""
This script contains the Prototype_5 class
This prototype is based entirely on technical analysis, and include new indicators, including:
    - EMA
    - LWMA

The following parameter_dictionary still require manual input:
    - spline interpolation coef
    - include trigger in signals (Technical_Indicators output generation)
    - buffer and buffer settings (Threshold determination)

Victor Guillet
12/14/2018
"""

from PhyTrade.Economic_model.Big_Data import BIGDATA
# ---> Import model settings
from SETTINGS import SETTINGS

# ---> Import indicators
from PhyTrade.Economic_model.Technical_Analysis.Technical_Indicators.RSI_gen import RSI
from PhyTrade.Economic_model.Technical_Analysis.Technical_Indicators.SMA_gen import SMA
from PhyTrade.Economic_model.Technical_Analysis.Technical_Indicators.EMA_gen import EMA
from PhyTrade.Economic_model.Technical_Analysis.Technical_Indicators.LWMA_gen import LWMA

# ---> Import amplification signals
from PhyTrade.Economic_model.Technical_Analysis.Amplification_signals.Volume_gen import VOLUME
from PhyTrade.Economic_model.Technical_Analysis.Amplification_signals.Volatility_gen import VOLATILITY

# ---> import general tools
from PhyTrade.Economic_model.MAJOR_SPLINE_gen import MAJOR_SPLINE
from PhyTrade.Tools.MATH_tools import MATH_tools
from PhyTrade.Economic_model.Technical_Analysis.Tools.OC_tools import OC
from PhyTrade.Tools.SPLINE_tools import SPLINE

import numpy as np
import time
import sys


class Prototype_5:
    def __init__(self, parameter_dictionary, data_slice):
        """
        Generate a model containing all coded indicators, process and generate bullish/bearish signals

        :param parameter_dictionary: Dictionary of dictionaries containing the values for all the variables of each signal
        :param data_slice: data_slice class instance
        """

        # ========================= ANALYSIS INITIALISATION ==============================
        # --> Fetch model settings
        settings = SETTINGS()
        settings.gen_model_settings()

        # --> Initiate records
        self.big_data = BIGDATA(data_slice)

        # ~~~~~~~~~~~~~~~~~~ Tools initialisation
        self.big_data.spline_multiplication_coef = settings.spline_interpolation_factor

        self.oc_tools = OC()
        self.spline_tools = SPLINE(self.big_data)
        self.math_tools = MATH_tools()

        # ~~~~~~~~~~~~~~~~~~ Technical_Indicators initialisation
        # -- RSI initialisation
        self.big_data.rsi_indicators = []
        for i in range(parameter_dictionary["indicators_count"]["rsi"]):
            self.big_data.rsi_indicators.append(RSI(self.big_data,
                                                    timeframe=parameter_dictionary["indicator_properties"]["timeframes"]["rsi_"+str(i)],
                                                    standard_upper_threshold=parameter_dictionary["indicator_properties"]["rsi_standard_upper_thresholds"]["rsi_" + str(i)],
                                                    standard_lower_threshold=parameter_dictionary["indicator_properties"]["rsi_standard_lower_thresholds"]["rsi_" + str(i)],
                                                    buffer_setting=settings.buffer_setting))

        # -- SMA initialisation
        self.big_data.sma_indicators = []
        for i in range(parameter_dictionary["indicators_count"]["sma"]):
            self.big_data.sma_indicators.append(SMA(self.big_data,
                                                    timeperiod_1=parameter_dictionary["indicator_properties"]["timeframes"]["sma_"+str(i)+"_1"],
                                                    timeperiod_2=parameter_dictionary["indicator_properties"]["timeframes"]["sma_"+str(i)+"_2"]))

        # -- EMA initialisation
        self.big_data.ema_indicators = []
        for i in range(parameter_dictionary["indicators_count"]["ema"]):
            self.big_data.ema_indicators.append(EMA(self.big_data,
                                                    timeperiod_1=parameter_dictionary["indicator_properties"]["timeframes"]["ema_"+str(i)+"_1"],
                                                    timeperiod_2=parameter_dictionary["indicator_properties"]["timeframes"]["ema_"+str(i)+"_2"]))

        # -- LWMA initialisation
        self.big_data.lwma_indicators = []
        for i in range(parameter_dictionary["indicators_count"]["lwma"]):
            self.big_data.lwma_indicators.append(LWMA(self.big_data,
                                                      timeperiod=parameter_dictionary["indicator_properties"]["timeframes"]["lwma_"+str(i)]))

        # ~~~~~~~~~~~~~~~~~~ Amplification signal initialisation
        # -- Volume initialisation
        self.big_data.volume = VOLUME(self.big_data,
                                      amplification_factor=parameter_dictionary["spline_property"]["amplification_factor"]["volume_0"])

        # -- Volatility initialisation
        self.big_data.volatility = VOLATILITY(self.big_data,
                                              timeframe=parameter_dictionary["indicator_properties"]["timeframes"]["volatility_0"],
                                              amplification_factor=parameter_dictionary["spline_property"]["amplification_factor"]["volatility_0"])

        # ================================================================================
        """




        """
        # ========================= DATA GENERATION AND PROCESSING =======================
        # ~~~~~~~~~~~~~~~~~~ Technical_Indicators output generation
        # -- RSI
        for indicator in self.big_data.rsi_indicators:
            indicator.get_output(self.big_data, include_triggers_in_bb_signal=settings.rsi_include_triggers_in_bb_signal)

        # -- SMA
        for indicator in self.big_data.sma_indicators:
            indicator.get_output(self.big_data, include_triggers_in_bb_signal=settings.sma_include_triggers_in_bb_signal)

        # -- EMA
        for indicator in self.big_data.ema_indicators:
            indicator.get_output(self.big_data, include_triggers_in_bb_signal=settings.ema_include_triggers_in_bb_signal)

        # -- LWMA
        for indicator in self.big_data.lwma_indicators:
            indicator.get_output(self.big_data, include_triggers_in_bb_signal=settings.lwma_include_triggers_in_bb_signal)

        # ~~~~~~~~~~~~~~~~~~ BB signals processing
        # ---> Creating splines from indicator signals
        # -- RSI
        self.big_data.rsi_splines = []
        for i in range(len(self.big_data.rsi_indicators)):
            self.big_data.rsi_splines.append(
            self.spline_tools.calc_signal_to_spline(self.big_data, self.big_data.rsi_indicators[i].bb_signal,
                                                    smoothing_factor=parameter_dictionary["spline_property"]["smoothing_factors"]["rsi_" + str(i)]))

        # -- SMA
        self.big_data.sma_splines = []
        for i in range(len(self.big_data.sma_indicators)):
            self.big_data.sma_splines.append(
            self.spline_tools.calc_signal_to_spline(self.big_data, self.big_data.sma_indicators[i].bb_signal,
                                                    smoothing_factor=parameter_dictionary["spline_property"]["smoothing_factors"]["sma_" + str(i)]))

        # -- EMA
        self.big_data.ema_splines = []
        for i in range(len(self.big_data.ema_indicators)):
            self.big_data.ema_splines.append(
            self.spline_tools.calc_signal_to_spline(self.big_data, self.big_data.ema_indicators[i].bb_signal,
                                                    smoothing_factor=parameter_dictionary["spline_property"]["smoothing_factors"]["ema_" + str(i)]))

        # -- LWMA
        self.big_data.lwma_splines = []
        for i in range(len(self.big_data.lwma_indicators)):
            self.big_data.lwma_splines.append(
            self.spline_tools.calc_signal_to_spline(self.big_data, self.big_data.lwma_indicators[i].bb_signal,
                                                    smoothing_factor=parameter_dictionary["spline_property"]["smoothing_factors"]["lwma_" + str(i)]))

        # -- OC avg gradient
        self.big_data.oc_gradient_splines = []
        self.big_data.oc_gradient_splines.append(
            self.spline_tools.calc_signal_to_spline(self.big_data, self.big_data.oc_avg_gradient_bb_signal,
                                                    smoothing_factor=parameter_dictionary["spline_property"]["smoothing_factors"]["oc_gradient_0"]))

        # ---> Generating amplification signals
        self.big_data.volume_splines = []
        self.big_data.volume_splines.append(
            self.spline_tools.calc_signal_to_spline(self.big_data, self.big_data.volume.amp_coef,
                                                    smoothing_factor=parameter_dictionary["spline_property"]["smoothing_factors"]["volume_0"]))

        self.big_data.volatility_splines = []
        self.big_data.volatility_splines.append(
            self.spline_tools.calc_signal_to_spline(self.big_data, self.big_data.volatility.amp_coef,
                                                    smoothing_factor=parameter_dictionary["spline_property"]["smoothing_factors"]["volatility_0"]))

        # ---> Tuning separate signals
        # TODO: Figure out a systematic way of flipping spline when necessary
        self.big_data.fliped_splines = []
        for flip in parameter_dictionary["spline_property"]["flip"]:
            if parameter_dictionary["spline_property"]["flip"][flip] is True:
                property_to_call = getattr(self.big_data, str(flip[:-1])+"splines")

                self.big_data.fliped_splines.append(self.spline_tools.flip_spline(property_to_call[int(flip[-1])]))
                print("spline flipped")

        # ---> Adding signals together
        # --> Creating signal array
        self.big_data.spline_array = np.array(self.big_data.oc_gradient_splines[0])

        for i in range(parameter_dictionary["indicators_count"]["rsi"]):
            np.vstack([self.big_data.spline_array, self.big_data.rsi_indicators[i]])

        for i in range(parameter_dictionary["indicators_count"]["sma"]):
            np.vstack([self.big_data.spline_array, self.big_data.sma_indicators[i]])

        for i in range(parameter_dictionary["indicators_count"]["ema"]):
            np.vstack([self.big_data.spline_array, self.big_data.ema_indicators[i]])

        for i in range(parameter_dictionary["indicators_count"]["lwma"]):
            np.vstack([self.big_data.spline_array, self.big_data.lwma_indicators[i]])

        sys.exit()

        for i in parameter_dictionary["spline_property"]["weights"]:
            break

        self.big_data.weights_array = np.array([[parameter_dictionary["weights"]["oc_avg_gradient_spline_weight"]],
                                               [parameter_dictionary["weights"]["rsi_1_spline_weight"]],
                                               [parameter_dictionary["weights"]["rsi_2_spline_weight"]],
                                               [parameter_dictionary["weights"]["rsi_3_spline_weight"]],
                                               [parameter_dictionary["weights"]["sma_1_spline_weight"]],
                                               [parameter_dictionary["weights"]["sma_2_spline_weight"]],
                                               [parameter_dictionary["weights"]["sma_3_spline_weight"]],
                                               [parameter_dictionary["weights"]["ema_1_spline_weight"]],
                                               [parameter_dictionary["weights"]["ema_2_spline_weight"]],
                                               [parameter_dictionary["weights"]["ema_3_spline_weight"]],
                                               [parameter_dictionary["weights"]["lwma_1_spline_weight"]],
                                               [parameter_dictionary["weights"]["lwma_2_spline_weight"]],
                                               [parameter_dictionary["weights"]["lwma_3_spline_weight"]]])

        self.big_data.combined_spline = \
            self.spline_tools.combine_splines(self.big_data.spline_array,
                                              self.big_data.weights_array)

        # ---> Tuning combined signal
        self.big_data.combined_spline = \
            self.spline_tools.modulate_amplitude_spline(
                self.big_data.combined_spline, self.big_data.spline_volume, std_dev_max=settings.volume_std_dev_max)

        self.big_data.combined_spline = \
            self.spline_tools.modulate_amplitude_spline(
                self.big_data.combined_spline, self.big_data.spline_volatility, std_dev_max=settings.volatility_std_dev_max)

        # print(self.big_data.combined_spline)
        # print(np.shape(self.big_data.combined_spline))

        self.big_data.combined_spline = self.math_tools.normalise_minus_one_one(self.big_data.combined_spline)

        # ~~~~~~~~~~~~~~~~~~ Threshold determination
        # ---> Creating dynamic thresholds
        upper_threshold, lower_threshold = \
            self.spline_tools.calc_thresholds(self.big_data, self.big_data.combined_spline,
                                              buffer=settings.buffer, buffer_setting=settings.buffer_setting,
                                              standard_upper_threshold=parameter_dictionary["major_spline_standard_upper_thresholds"]["major_spline_standard_upper_threshold"],
                                              standard_lower_threshold=parameter_dictionary["major_spline_standard_lower_thresholds"]["major_spline_standard_lower_threshold"])

        # ---> Modulating threshold with SMA 3 value
        # upper_threshold = self.spline_tools.modulate_amplitude_spline(
        #         upper_threshold,  self.math_tools.amplify(
        #             self.math_tools.normalise_zero_one(self.big_data.spline_sma_3), 0.3))
        #
        # lower_threshold = self.spline_tools.modulate_amplitude_spline(
        #         lower_threshold,  self.math_tools.amplify(
        #             self.math_tools.normalise_zero_one(self.big_data.spline_sma_3), 0.3))

        # ~~~~~~~~~~~~~~~~~~ Creating Major Spline/trigger values
        self.big_data.Major_spline = MAJOR_SPLINE(self.big_data,
                                                  upper_threshold, lower_threshold)

    # ================================================================================
    """




    """

    # ========================= SIGNAL PLOTS =========================================
    def plot(self, plot_1=True, plot_2=True, plot_3=True):
        """
        :param plot_1: Plot Open/Close prices & RSI
        :param plot_2: Plot Open/Close prices & SMA
        :param plot_3: Plot Open/Close prices & Bullish/Bearish signal
        """
        import matplotlib.pyplot as plt

        if plot_1:
            # ---------------------------------------------- Plot 1
            # ------------------ Plot Open/Close prices
            ax1 = plt.subplot(211)
            self.oc_tools.plot_oc_values(self.big_data)
            # oc.plot_trigger_values(self.big_data)

            # ------------------ Plot RSI
            ax2 = plt.subplot(212, sharex=ax1)
            self.big_data.rsi.plot_rsi(self.big_data)
            plt.show()

        if plot_2:
            # ---------------------------------------------- Plot 2
            # ------------------ Plot Open/Close prices
            ax3 = plt.subplot(211)
            self.oc_tools.plot_oc_values(self.big_data)
            # oc.plot_trigger_values(self.big_data)

            # ------------------ Plot SMA Signal
            ax4 = plt.subplot(212, sharex=ax3)
            self.big_data.sma_1.plot_sma(self.big_data, plot_trigger_signals=False)
            plt.show()

        if plot_3:
            # ---------------------------------------------- Plot 3
            # ------------------ Plot Open/Close prices
            ax5 = plt.subplot(211)
            self.oc_tools.plot_oc_values(self.big_data)
            self.oc_tools.plot_trigger_values(
                self.big_data, self.big_data.Major_spline.sell_dates, self.big_data.Major_spline.buy_dates)

            # ------------------ Plot bb signal(s)
            ax6 = plt.subplot(212)
            # ---> RSI signals
            # self.spline_tools.plot_spline(
            #     self.big_data, self.big_data.spline_rsi_1, label="RSI bb spline")
            # self.spline_tools.plot_spline(
            #     self.big_data, self.big_data.spline_rsi_2, label="RSI bb spline")
            # self.spline_tools.plot_spline(
            #     self.big_data, self.big_data.spline_rsi_3, label="RSI bb spline")

            # ---> OC gradient signals
            # self.spline_tools.plot_spline(
            #     self.big_data, self.big_data.spline_oc_avg_gradient, label="OC gradient bb spline", color='m')

            # ---> SMA signals
            # self.spline_tools.plot_spline(
            #     self.big_data, self.big_data.spline_sma_1, label="SMA_1 bb spline", color='b')
            # self.spline_tools.plot_spline(
            #     self.big_data, self.big_data.spline_sma_2, label="SMA_2 bb spline", color='b')
            # self.spline_tools.plot_spline(
            #     self.big_data, self.big_data.spline_sma_3, label="SMA_3 bb spline", color='r')

            # # ---> EMA signals
            # self.spline_tools.plot_spline(
            #     self.big_data, self.big_data.spline_ema_1, label="EMA_1 bb spline", color='b')
            # self.spline_tools.plot_spline(
            #     self.big_data, self.big_data.spline_ema_2, label="EMA_2 bb spline", color='b')
            # self.spline_tools.plot_spline(
            #     self.big_data, self.big_data.spline_ema_3, label="EMA_3 bb spline", color='r')

            # ---> LWMA signals
            # self.spline_tools.plot_spline(
            #     self.big_data, self.big_data.spline_lwma_1, label="LWMA_1 bb spline", color='b')
            # self.spline_tools.plot_spline(
            #     self.big_data, self.big_data.spline_lwma_2, label="LWMA_2 bb spline", color='b')
            # self.spline_tools.plot_spline(
            #     self.big_data, self.big_data.spline_lwma_3, label="LWMA_3 bb spline", color='r')

            self.spline_tools.plot_spline(
                self.big_data, self.big_data.Major_spline.spline, label="Major spline", color='y')

            self.spline_tools.plot_spline(
                self.big_data, self.big_data.Major_spline.upper_threshold, label="Upper threshold")
            self.spline_tools.plot_spline(
                self.big_data, self.big_data.Major_spline.lower_threshold, label="Lower threshold")

            self.spline_tools.plot_spline_trigger(
                self.big_data, self.big_data.Major_spline.spline, self.big_data.Major_spline.sell_dates,
                self.big_data.Major_spline.buy_dates)

            # self.spline_tools.plot_spline(self.big_data, self.big_data.spline_volume, label="Volume", color='k')
            # self.spline_tools.plot_spline(self.big_data, self.big_data.spline_volatility, label="Volatility", color='grey')

            plt.legend()
            plt.show()

        return
