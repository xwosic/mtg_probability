import getopt
import sys
import math
import os
from pprint import pprint


class MtgCalc:
    """
    MtgCalc class instances can calculate probability
    of drawing X cards of the specific number of those cards from deck.
    """
    def __init__(self, commandline_args):
        """
        Creating instance of MtgCalc and validating provided options.
        :param commandline_args: command line arguments without first one - name of module
        """
        self._options, self._arguments = self._get_commandline_args(commandline_args)
        try:
            if '-f' in self._options:
                self._path_to_file_with_decklist = self._options['-f']
                self._decklist_lines = []
                self._decklist_by_cmc = []
                self.land_results = {}
                self.cmc_results = {}
                self.result_probability_of_both = {}
                self._statistic_mode = True

                self.num_of_cards = 99
                self.num_of_desired_cards_in_deck = 1
                self.num_of_draws = 1
                self.success_when = 1
            else:
                self.num_of_cards = int(self._options['-c'])
                self.num_of_desired_cards_in_deck = int(self._options['-n'])
                self.num_of_draws = int(self._options['-d'])
                self.success_when = int(self._options['-s'])
                self._statistic_mode = False

            self.probability = 0
        except (ValueError, TypeError):
            sys.exit("All provided options has to be of type positive integer.")

    @staticmethod
    def _newtons_symbol(n, k):
        """
        Staticmethod calculating Newton's symbol.
        In other words: Method calculates number of combinations
        without repeat from the n-element set
        :param n: size of set
        :param k: size of sample took from set
        :return: number of possible combinations
        """
        return math.factorial(n) // (math.factorial(k) * math.factorial(n - k))

    def calculate_probability(self, success=-1):
        """
        Method calculating hypergeometric distribution.
        :return: Propability of case returned as decimal number from 0.0 to 1.0
        """
        if success == -1:
            success = self._success_when

        k_from_K = self._newtons_symbol(self._num_of_desired_cards_in_deck, success)
        n_from_N = self._newtons_symbol(self._num_of_cards, self._num_of_draws)
        other = self._newtons_symbol(self._num_of_cards - self._num_of_desired_cards_in_deck, self._num_of_draws - success)
        return k_from_K * other / n_from_N

    def calculate_cumulative_probability(self):
        """
        Iterating through every possible scenario of drawing cards
        and calculating chances for drawing X >= when_success cards.
        :return: probability of drawing x>= when_success
        """
        probability_of_less_than_x = 0.0
        for i in range(self._success_when):
            probability_of_less_than_x += self.calculate_probability(i)

        return 1 - probability_of_less_than_x

    def calculate_num_of_cards_in_deck(self, probability, after_x_draws):
        # Likelihood of NOT drawing minimum 1 desired card
        prob_of_failure = (1 - probability)**(1 / after_x_draws)
        # Likelihood of drawing minimum 1 desired card
        prob_of_success = 1 - prob_of_failure
        # That many desired cards has to be in deck
        minimum_of_desired_cards = prob_of_success * self._num_of_cards
        return round(minimum_of_desired_cards)

    def _get_commandline_args(self, commandline_args):
        """
        Method takes command line arguments and parses it to dict and list.
        If help option was provided method prints help info and ends programme.
        :param commandline_args: command line arguments without first one - name of module
        :return: tuple of dict of options and list of arguments
        """
        try:
            options, arguments = getopt.getopt(commandline_args, "hc:d:n:s:f:")

            opt_dir = {}
            for option in options:
                opt_dir[option[0]] = option[1]

        except (getopt.GetoptError, TypeError) as er:
            print(er)
            sys.exit()

        else:
            # no args
            if len(opt_dir) == 0:
                self.show_help()
            # help arg
            if '-h' in opt_dir or '--help' in opt_dir:
                self.show_help()
            # not exactly 4 args
            # if len(opt_dir) != 4:
            #     print('There should be 4 options provided.')
            #     self.show_help()

            return opt_dir, arguments

    def read_decklist_from_file(self):
        if os.path.exists(self._path_to_file_with_decklist):
            if os.path.isfile(self._path_to_file_with_decklist):
                try:
                    f = open(self._path_to_file_with_decklist, 'r')
                    self._decklist_lines = f.read().splitlines()
                    # pprint(self._decklist_lines)

                except (PermissionError, FileExistsError, FileNotFoundError) as er:
                    print(er)

                finally:
                    f.close()

            else:
                sys.exit(f'Not a file: {self._path_to_file_with_decklist}')

        else:
            sys.exit(f'Incorrect path to file: {self._path_to_file_with_decklist}')

    def parse_to_cmc(self):
        content_dict = {}
        mc_dict = {}
        current_category = 'no category'
        mana_curve = False
        for line in self._decklist_lines:
            if len(line) > 0 and not line.isspace():
                # new category
                if line.startswith('#'):
                    continue

                if line.startswith('['):
                    if line.startswith('[MANA CURVE]'):
                        mana_curve = True

                    current_category = self._convert_to_category_key(line)
                    if not mana_curve:
                        content_dict[current_category] = []
                    else:
                        mc_dict[current_category] = []

                # next from category
                else:
                    if not mana_curve:
                        self._add_to_dict(content_dict, current_category, self.create_tuple_name_number(line))
                    else:
                        self._add_to_dict(mc_dict, current_category, self.create_tuple_name_number(line))

        self._decklist_by_cmc = content_dict

    @staticmethod
    def create_tuple_name_number(line):
        line = line.rstrip()
        number = [int(i) for i in line.split() if i.isdigit()]
        if len(number) == 1:
            number = number[0]
        name = line.replace(str(number), '')
        name = name.lstrip()
        return name, number

    @staticmethod
    def _convert_to_category_key(line):
        line = line.lower()
        line = line.replace('[', '')
        line = line.replace(']', '')
        line = line.rstrip()
        return line

    @staticmethod
    def _add_to_dict(my_dict, key, value):
        if key in my_dict:
            my_dict[key] = my_dict[key] + [value]

        else:
            my_dict[key] = [value]

    def calculate_statistics(self):
        # get sizes of categories
        for category in self._decklist_by_cmc:
            self._decklist_by_cmc[category] = {'cards': self._decklist_by_cmc[category],
                                               'size': self._count_cards_in_list(self._decklist_by_cmc[category])}

        self._prepare_environment()
        # calculate probability of playing card with cmc equal turn's number
        cmc_results = {
            1: 0,
            2: 0,
            3: 0,
            4: 0,
            5: 0,
            6: 0,
            7: 0
        }
        for turn in cmc_results:
            key = str('cost ' + str(turn))
            if key in self._decklist_by_cmc:
                self._success_when = 1
                self._num_of_desired_cards_in_deck = self._decklist_by_cmc[key]['size']
                self._num_of_draws = 6 + turn
                cmc_results[turn] = self.calculate_cumulative_probability()

            else:
                key = key + "+"
                if key in self._decklist_by_cmc:
                    self._success_when = 1
                    self._num_of_desired_cards_in_deck = self._decklist_by_cmc[key]['size']
                    self._num_of_draws = 6 + turn
                    cmc_results[turn] = self.calculate_cumulative_probability()

        # calculate probability of playing land every turn to x turn
        land_results = {
            1: 0,
            2: 0,
            3: 0,
            4: 0,
            5: 0,
            6: 0,
            7: 0
        }
        for turn in land_results:
            self._success_when = turn
            self._num_of_desired_cards_in_deck = self._decklist_by_cmc['lands']['size']
            self._num_of_draws = 6 + turn
            land_results[turn] = self.calculate_cumulative_probability()

        result_probability_of_both = {}
        key_both = 1
        for l_result, cmc_result in zip(land_results.values(), cmc_results.values()):
            result_probability_of_both[key_both] = l_result * cmc_result
            key_both += 1

        self.land_results = land_results
        self.cmc_results = cmc_results
        self.result_probability_of_both = result_probability_of_both

    def calculate_statistics_by_dict(self, my_dict):
        # get sizes of categories
        for category in my_dict:
            my_dict[category] = {'cards': my_dict[category],
                                 'size': self._count_cards_in_list(my_dict[category])}

        self._prepare_environment()
        # calculate probability of playing card with cmc equal turn's number
        cmc_results = {
            1: 0,
            2: 0,
            3: 0,
            4: 0,
            5: 0,
            6: 0,
            7: 0
        }
        streak_cmc_results = {
            1: 1,
            2: 1,
            3: 1,
            4: 1,
            5: 1,
            6: 1,
            7: 1
        }
        for turn in cmc_results:
            key = str('cost ' + str(turn))
            if key in my_dict:
                self._success_when = 1
                self._num_of_desired_cards_in_deck = my_dict[key]['size']
                self._num_of_draws = 6 + turn
                cmc_results[turn] = self.calculate_cumulative_probability()
                streak_cmc_results[turn] = cmc_results[turn] * streak_cmc_results[turn]

            else:
                key = key + "+"
                if key in my_dict:
                    self._success_when = 1
                    self._num_of_desired_cards_in_deck = my_dict[key]['size']
                    self._num_of_draws = 6 + turn
                    cmc_results[turn] = self.calculate_cumulative_probability()

        pprint(streak_cmc_results)
        # calculate probability of playing land every turn to x turn
        land_results = {
            1: 0,
            2: 0,
            3: 0,
            4: 0,
            5: 0,
            6: 0,
            7: 0
        }
        for turn in land_results:
            self._success_when = turn
            self._num_of_desired_cards_in_deck = my_dict['lands']['size']
            self._num_of_draws = 6 + turn
            land_results[turn] = self.calculate_cumulative_probability()

        result_probability_of_both = {}
        key_both = 1
        for l_result, cmc_result in zip(land_results.values(), cmc_results.values()):
            result_probability_of_both[key_both] = l_result * cmc_result
            key_both += 1

        self.land_results = land_results
        self.cmc_results = cmc_results
        self.result_probability_of_both = result_probability_of_both

    def create_output_strings(self):
        output = '\t\t1ST TURN\t2ND TURN\t3RD TURN\t4TH TURN\t5TH TURN\t6TH TURN\t7TH TURN\n'
        output = output + 'LAND STREAK\t'
        for probability in self.land_results.values():
            probability = round(probability, 2)
            output += "{:<16}".format(probability)

        output = output + '\nCMC = TURN\t'
        for probability in self.cmc_results.values():
            probability = round(probability, 2)
            output += "{:<16}".format(probability)

        output = output + '\nSTREAK BOTH\t'
        for probability in self.result_probability_of_both.values():
            probability = round(probability, 2)
            output += "{:<16}".format(probability)

        print(output)

    @staticmethod
    def _count_cards_in_list(input_list_of_tuple):
        cards_sum = 0
        for name, number in input_list_of_tuple:
            cards_sum += number

        return cards_sum

    def _prepare_environment(self):
        # all cards
        sum_sizes = 0
        for category in self._decklist_by_cmc:
            # ignores sideboard, maybeboard and commander
            if category not in ('sideboard', 'maybeboard', 'commander'):
                sum_sizes += self._decklist_by_cmc[category]['size']

        self._num_of_cards = sum_sizes

    @staticmethod
    def show_help():
        """
        Prints help information to console and exits programme.
        :return: SystemExit
        """
        sys.exit("Syntax: mtg_prob -c <int> -d <int> -n <int> -s <int>\n"
        		 "Syntax: mtg_prob -f <path_to_deck_list_txt>\n"
                 "Options:\n"
                 "\t-c          Number of cards in deck\n"
                 "\t-d          Number of draws\n"
                 "\t-n          Number of cards in deck which are desired\n"
                 "\t-s          Number of desired cards drew to achieve success\n"
                 "\t-f          Path to file with deck list")

    @property
    def num_of_cards(self):
        return self._num_of_cards

    @num_of_cards.setter
    def num_of_cards(self, value):
        if isinstance(value, int):
            if value > 0:
                self._num_of_cards = value
            else:
                raise ValueError("Number of cards in deck has to be bigger than 0")
        else:
            raise TypeError("Number of cards has to be of type int")

    @property
    def num_of_desired_cards_in_deck(self):
        return self._num_of_desired_cards_in_deck

    @num_of_desired_cards_in_deck.setter
    def num_of_desired_cards_in_deck(self, value):
        if isinstance(value, int):
            if value > 0:
                self._num_of_desired_cards_in_deck = value
            else:
                raise ValueError("num_of_desired_cards_in_deck in deck has to be bigger than 0")
        else:
            raise TypeError("num_of_desired_cards_in_deck has to be of type int")

    @property
    def num_of_draws(self):
        return self._num_of_draws

    @num_of_draws.setter
    def num_of_draws(self, value):
        if isinstance(value, int):
            if value > 0:
                self._num_of_draws = value
            else:
                raise ValueError("num_of_draws in deck has to be bigger than 0")
        else:
            raise TypeError("num_of_draws has to be of type int")

    @property
    def success_when(self):
        return self._success_when

    @success_when.setter
    def success_when(self, value):
        if isinstance(value, int):
            if value > 0:
                self._success_when = value
            else:
                raise ValueError("success_when in deck has to be bigger than 0")
        else:
            raise TypeError("success_when has to be of type int")

    @property
    def probability(self):
        return self._probability

    @probability.setter
    def probability(self, value):
        if isinstance(value, int):
            if value >= 0:
                self._probability = value
            else:
                raise ValueError("probability has to be bigger than 0")
        else:
            raise TypeError("probability has to be of type int")

    @property
    def statistic_mode(self):
        return self._statistic_mode


def main():
    mtg = MtgCalc(sys.argv[1:])
    if not mtg.statistic_mode:
        print(f"Number of cards in deck: {mtg.num_of_cards}\n"
              f"Number of draws (starting player turn {mtg.num_of_draws - 6}, other's turn "
              f"{mtg.num_of_draws -7}): {mtg.num_of_draws}\n"
              f"Number of cards in deck which are desired: {mtg.num_of_desired_cards_in_deck}\n"
              f"Minimum number of desired cards drew to achieve success: {mtg.success_when}")
        print("Possibility of achieving that: %.2f%%" % (mtg.calculate_cumulative_probability() * 100))

    else:
        # head, tail = os.path.split(mtg._path_to_file_with_decklist)
        # deck_name = tail.split('.')
        # print(deck_name[0])
        print('')
        # read from file
        mtg.read_decklist_from_file()
        # parse content
        mtg.parse_to_cmc()
        # print stats
        mtg.calculate_statistics()
        mtg.create_output_strings()
        print('')


if __name__ == "__main__":
    main()
