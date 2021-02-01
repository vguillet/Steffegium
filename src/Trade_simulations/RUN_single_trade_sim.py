
################################################################################################################
"""
Contains the EVAL_parameter_set class, to be used for direct evaluation of a set of parameters over a specific data slice

Input that still require manual input:
    - Metalabels settings
    - Investment settings
    - Stop-loss settings
"""

# Built-in/Generic Imports
import math
import pprint

# Own modules
from src.Settings.SETTINGS import SETTINGS
from src.Tools.Progress_bar_tool import Progress_bar
from src.Building_blocks.Trading_dataslice import Trading_dataslice
from src.Building_blocks.Individual import Individual
from src.Signal_optimisation.EVO_algorithm.Tools.Throttle_tool import throttle

__version__ = '1.1.1'
__author__ = 'Victor Guillet'
__date__ = '10/09/2019'

################################################################################################################


class RUN_single_trade_sim:
    def __init__(self):

        # ~~~~~~~~~~~~~~~~ Dev options ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        settings = SETTINGS()
        # ---- Fetch single_trade_sim settings
        settings.market_settings.gen_market_settings()

        ticker = settings.market_settings.tickers[0]
        parameter_set = settings.market_settings.parameter_sets[0]

        start_date = settings.market_settings.testing_start_date
        end_date = settings.market_settings.testing_end_date
        subslice_size = settings.market_settings.subslice_size

        # --> Simulation parameters
        settings.trade_sim_settings.gen_single_trade_sim()
        settings.tradebot_settings.gen_tradebot_settings()
        
        eval_name = settings.trade_sim_settings.simulation_name
        nb_data_slices = settings.trade_sim_settings.nb_data_slices

        # --> Print/Plot parameters
        print_trade_process = settings.trade_sim_settings.print_trade_process
        plot_eco_model_results = settings.trade_sim_settings.plot_eco_model_results

        # ---- Fetch Metalabeling settings
        settings.metalabeling_settings.gen_metalabels_settings()

        run_metalabels = settings.trade_sim_settings.run_metalabels         # Can be switched off for performance increase

        metalabeling_setting = settings.metalabeling_settings.metalabeling_setting

        upper_barrier = settings.metalabeling_settings.upper_barrier
        lower_barrier = settings.metalabeling_settings
        look_ahead = settings.metalabeling_settings.look_ahead

        m_investment_settings = settings.trade_sim_settings.m_investment_settings
        m_cash_in_settings = settings.trade_sim_settings.m_cash_in_settings

        # --> Investment settings
        investment_settings = settings.trade_sim_settings.investment_settings
        cash_in_settings = settings.trade_sim_settings.cash_in_settings

        max_investment_per_trade_percent = settings.trade_sim_settings.max_investment_per_trade_percent
        min_investment_per_trade_percent = settings.trade_sim_settings.min_investment_per_trade_percent

        investment_per_trade_decay_function = settings.trade_sim_settings.investment_per_trade_decay_function

        # --> Stop-loss settings
        max_prev_stop_loss = settings.trade_sim_settings.max_prev_stop_loss
        min_prev_stop_loss = settings.trade_sim_settings.min_prev_stop_loss

        prev_stop_loss_decay_function = settings.trade_sim_settings.prev_stop_loss_decay_function

        max_max_stop_loss = settings.trade_sim_settings.max_max_stop_loss
        min_max_stop_loss = settings.trade_sim_settings.min_max_stop_loss

        max_stop_loss_decay_function = settings.trade_sim_settings.max_stop_loss_decay_function

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        # ---- Initiate run parameters
        self.ticker = ticker
        self.parameter_set = parameter_set

        # ---- Current param setup
        # Finance
        self.current_funds = settings.tradebot_settings.initial_investment
        self.current_net_worth = self.current_funds
        self.current_assets = 0
        self.current_simple_investment_assets = None

        self.max_investment_per_trade = settings.trade_sim_settings.max_investment_per_trade_percent

        # Metalabel finance:
        if run_metalabels:
            self.m_current_funds = settings.tradebot_settings.initial_investment
            self.m_current_net_worth = self.current_funds
            self.m_current_assets = 0

        # stop-losses
        self.prev_stop_loss = settings.trade_sim_settings.max_prev_stop_loss
        self.max_stop_loss = settings.trade_sim_settings.max_max_stop_loss

        # ---- Initiate records
        self.results = Trade_simulation_results_gen(eval_name)

        # ---- Initiate data slice
        self.data_slice = Trading_dataslice(ticker=self.ticker,
                                            start_date=start_date,
                                            subslice_size=subslice_size,
                                            subslice_shift_per_step=0,
                                            end_date=end_date,
                                            data_looper=False)

        self.data_slice.gen_subslice_metalabels(upper_barrier=upper_barrier,
                                                lower_barrier=lower_barrier,
                                                look_ahead=look_ahead,
                                                metalabeling_setting=metalabeling_setting)

        self.nb_data_slices = math.ceil(abs(self.data_slice.start_index-self.data_slice.end_index)/subslice_size)
        
        # ---- Generate Individual
        self.individual = Individual(parameter_set=parameter_set)

        # ===============================================================================
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print("Single ticker Trade simulation \n")

        print("Evaluated ticker:", ticker)
        print("\nStart date:", start_date)
        print("Data slice size:", subslice_size)
        print("Number of data slices processed:", nb_data_slices)
        print("\nStarting parameters:")
        pprint.pprint(parameter_set)

        print("\nInvestment_settings =", investment_settings)
        print("Cash-in settings =", cash_in_settings)
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
        # ============================ TRADING SIMULATION ===============================
        # ---- Generate economic model and perform trade run for all data slices
        progress_bar = Progress_bar(self.nb_data_slices, bar_size=40, label="Simulation progress", overwrite_setting=False)

        data_slice_count = 0
        while self.data_slice.end_of_dataset is False:
            data_slice_count += 1

            print("================== Data slice", data_slice_count, "==================")
            print(self.data_slice.start_date, "-->", self.data_slice.subslice_stop_date)

            # --> Process slice metalabels
            if run_metalabels is True:
                self.data_slice.gen_subslice_metalabels(upper_barrier=upper_barrier,
                                                        lower_barrier=lower_barrier,
                                                        look_ahead=look_ahead,
                                                        metalabeling_setting=metalabeling_setting)

                self.data_slice.perform_metatrade_run(investment_settings=m_investment_settings,
                                                      cash_in_settings=m_cash_in_settings,
                                                      initial_funds=self.m_current_funds,
                                                      initial_assets=self.m_current_assets,
                                                      prev_stop_loss=self.prev_stop_loss,
                                                      max_stop_loss=self.max_stop_loss,
                                                      max_investment_per_trade=self.max_investment_per_trade * self.m_current_net_worth,
                                                      prev_simple_investment_assets=self.current_simple_investment_assets)

                self.results.metalabel_net_worth += self.data_slice.metalabels_account.net_worth_history

            # --> Process slice
            self.individual.gen_economic_model(data_slice=self.data_slice,
                                               plot_eco_model_results=plot_eco_model_results)

            self.individual.perform_trade_run(data_slice=self.data_slice,
                                              investment_settings=investment_settings,
                                              cash_in_settings=cash_in_settings,
                                              initial_funds=self.current_funds,
                                              initial_assets=self.current_assets,
                                              prev_stop_loss=self.prev_stop_loss,
                                              max_stop_loss=self.max_stop_loss,
                                              max_investment_per_trade=self.max_investment_per_trade * self.current_net_worth,
                                              prev_simple_investment_assets=self.current_simple_investment_assets,
                                              print_trade_process=print_trade_process)

            # --> Record slice trade history
            # --> Record trade actions
            self.results.buy_count += self.individual.tradebot.buy_count
            self.results.sell_count += self.individual.tradebot.sell_count

            self.results.stop_loss_count += self.individual.tradebot.stop_loss_count

            # --> Record finance
            self.results.funds += self.individual.account.funds_history
            self.results.net_worth += self.individual.account.net_worth_history
            self.results.profit.append((self.individual.account.net_worth_history[-1]-self.current_net_worth)/self.current_net_worth*100)

            self.results.assets += self.individual.account.assets_history
            self.results.simple_investment += self.individual.account.simple_investment_net_worth

            # --> Record model
            self.results.trade_spline += list(self.individual.analysis.trade_spline)
            self.results.trade_signal += list(self.individual.analysis.trade_signal)
            self.results.major_upper_threshold += list(self.individual.analysis.major_upper_threshold)
            self.results.major_lower_threshold += list(self.individual.analysis.major_lower_threshold)
            self.results.metalabels += list(self.data_slice.metalabels)

            # --> Print Data slice results
            print("--------------------------------------------------")
            print("Net worth =", round(self.results.net_worth[-1]), "$; Simple investment worth=", self.results.simple_investment[-1])
            print("Buy count:", self.individual.tradebot.buy_count,
                  "; Sell count:", self.individual.tradebot.sell_count,
                  "; Stop loss count:", self.individual.tradebot.stop_loss_count, "\n")
            progress_bar.update_progress()
            print("\n--------------------------------------------------")

            # ---- Calc next data slice parameters and stop simulation if end date reached
            self.data_slice.get_next_subslice()
            if self.data_slice.end_of_dataset:
                break

            # --> Update current parameters
            self.current_funds = self.individual.account.funds_history[-1]
            self.current_assets = self.individual.account.assets_history[-1]
            self.current_net_worth = self.individual.account.net_worth_history[-1]
            self.current_simple_investment_assets = self.individual.account.simple_investment_assets

            if run_metalabels:
                self.m_current_funds = self.data_slice.metalabels_account.funds_history[-1]
                self.m_current_assets = self.data_slice.metalabels_account.assets_history[-1]
                self.m_current_net_worth = self.data_slice.metalabels_account.assets_history[-1]

            # --> Throttle values
            self.prev_stop_loss = round(throttle(current_iteration=data_slice_count,
                                                 nb_of_iterations=self.nb_data_slices,
                                                 max_value=max_prev_stop_loss,
                                                 min_value=min_prev_stop_loss,
                                                 decay_function=prev_stop_loss_decay_function), 3)

            self.max_stop_loss = round(throttle(current_iteration=data_slice_count,
                                                nb_of_iterations=self.nb_data_slices,
                                                max_value=max_max_stop_loss,
                                                min_value=min_max_stop_loss,
                                                decay_function=max_stop_loss_decay_function), 3)

            self.max_investment_per_trade = round(throttle(current_iteration=data_slice_count,
                                                           nb_of_iterations=self.nb_data_slices,
                                                           max_value=max_investment_per_trade_percent,
                                                           min_value=min_investment_per_trade_percent,
                                                           decay_function=investment_per_trade_decay_function), 3)

            # --> Print throttled values
            print("Next slice parameters:")
            print("Prev stop loss", self.prev_stop_loss)
            print("Max stop loss", self.max_stop_loss)
            print("Max investment per trade", self.max_investment_per_trade, "\n")

        # ---- Generate simulation summary
        self.results.ticker = self.ticker
        self.results.individual = self.individual
        self.parameter_set = self.parameter_set

        self.results.data_slice_start_date = self.data_slice.start_date
        self.results.data_slice_stop_date = self.data_slice.end_date
        self.results.data_slice_size = self.data_slice.subslice_size
        self.results.nb_data_slices = self.nb_data_slices

        self.results.total_data_points_processed = abs(self.data_slice.start_index-self.data_slice.end_index)

        self.results.gen_result_recap_file()

        if settings.trade_sim_settings.plot_eco_model_results:
            self.results.plot_results(settings=settings,
                                      big_data=self.individual.analysis.big_data,
                                      run_metalabels=run_metalabels)

        print("-- Trade simulation completed --")
        print("Number of data points processed:", self.results.total_data_points_processed)


class Trade_simulation_results_gen:
    def __init__(self, run_label):
        self.run_label = "Trade_simulation_" + run_label

        self.ticker = None
        self.individual = None
        self.parameter_set = None

        self.data_slice_start_date = None
        self.data_slice_stop_date = None
        self.data_slice_size = None
        self.nb_data_slices = None

        self.benchmark_confusion_matrix_analysis = None
        self.total_data_points_processed = None

        # --> Trade history
        self.buy_count = 0
        self.sell_count = 0
        self.stop_loss_count = 0

        # --> Finance history
        self.net_worth = []
        self.profit = []
        self.funds = []
        self.assets = []

        self.simple_investment = []
        self.metalabel_net_worth = []

        # --> Model history
        self.trade_spline = []
        self.trade_signal = []
        self.major_upper_threshold = []
        self.major_lower_threshold = []
        self.metalabels = []

    def gen_result_recap_file(self):
        # -- Create results file
        path = r"Data\RUN_trade_sim_results".replace('\\', '/')
        full_file_name = path + '/' + self.run_label

        self.results_file = open(full_file_name + ".txt", "w+")

        self.results_file.write("====================== " + self.run_label + " ======================\n")
        self.results_file.write("\n-----------> Model settings:" + "\n")
        self.results_file.write("Ticker: " + str(self.ticker) + "\n")
        self.results_file.write("\ndata_slice_start_date = " + str(self.data_slice_start_date))
        self.results_file.write("\ndata_slice_end_date = " + str(self.data_slice_stop_date) + "\n")
        self.results_file.write("data_slice_size = " + str(self.data_slice_size) + "\n")
        self.results_file.write("nb_data_slices = " + str(self.nb_data_slices) + "\n")
        self.results_file.write("Model parameters: " + str(self.parameter_set) + "\n")

        self.results_file.write("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
        self.results_file.write("-----------> Run stats: \n")
        self.results_file.write("\nNumber of data points processed: " + str(self.total_data_points_processed) + "\n")
        self.results_file.write("Buy trigger count: " + str(self.buy_count) + "\n")
        self.results_file.write("Sell trigger count: " + str(self.sell_count) + "\n")

        self.results_file.write("\nFinal net worth: " + str(round(self.net_worth[-1])) + "$\n")
        self.results_file.write("Average profit per gen: " + str(round(sum(self.profit)/len(self.profit))) + "%\n")
        self.results_file.write("Max profit achieved: " + str(round(max(self.profit))) + "%\n")
        if min(self.profit) >= 0:
            self.results_file.write("Min profit achieved: " + str(round(min(self.profit))) + "%\n")
        else:
            self.results_file.write("Max loss achieved: " + str(round(min(self.profit))) + "%\n")

        self.results_file.write("\nSimple investment final net worth: " + str(round(self.simple_investment[-1])) + "$\n")
        self.results_file.write("Simple investment profit: " + str(round((self.simple_investment[-1]-1000)/1000*100)) + "%\n")

        self.results_file.write(
            "\n Net worth difference trading strategy vs simple investment: " + str(round(self.net_worth[-1]-self.simple_investment[-1])) + "$\n")
        self.results_file.write(
            "% Net worth difference trading strategy vs simple investment: " + str(round((self.net_worth[-1] - self.simple_investment[-1])/self.simple_investment[-1]*100)) + "%\n")
        # self.results_file.write("" + "\n")
        self.results_file.write("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")

        self.results_file.write(str() + "\n")

        self.results_file.close()

    def plot_results(self, settings, big_data, run_metalabels):
        import matplotlib.pyplot as plt
        from src.Tools.Plot_tools import Plot_tools

        # --> Plot trade results
        plt.plot(self.net_worth, label="Net worth")
        plt.plot(self.funds, label="Funds")
        plt.plot(self.assets, label="Assets")
        plt.plot(self.simple_investment, label="Simple investment NW")

        if run_metalabels:
            plt.plot(self.metalabel_net_worth, label="Metalabels NW")

        plt.grid()
        plt.legend()

        plt.show()

        # --> Plot model results
        print_data_slice = Trading_dataslice(ticker=self.ticker,
                                             start_date=self.data_slice_start_date,
                                             subslice_size=self.total_data_points_processed,
                                             subslice_shift_per_step=0)

        Plot_tools().plot_trade_process(settings=settings,
                                        data_slice=print_data_slice,
                                        trade_spline=self.trade_spline,
                                        trade_upper_threshold=self.major_upper_threshold,
                                        trade_lower_threshold=self.major_lower_threshold,
                                        trade_signal=self.trade_signal,
                                        trading_indicators=big_data.content["trading_indicator_splines"])
        return
