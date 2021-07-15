# Magic the Gathering Probability Calculator
## Description
This is command line tool to calculate probability of accieving success by drawing X desired cards from deck.
To get result script uses [hypergeometric distribution](https://en.wikipedia.org/wiki/Hypergeometric_distribution).

## Usage
There are two possible ways to use this script:
 * by providing command line arguments
 * by providing path to decklist

## Arguments
 * -c Number of cards in deck
 * -d Number of draws
 * -n Number of cards in deck which are desired
 * -s Number of desired cards drew to achieve success\
 `python -m mtg_prob -c 60 -d 12 -n 4 -s 1`

## Path to decklist
 * -f Path to file with deck list\
 `python -m mtg_prob -f Reap_the_Tide_example.txt`\
 Cards in sideboard, maybeboard and commander are ignored.

### This functionality returns a table of probabilities per turn of such events as:
 * LAND STREAK - an event when player plays land card every turn since beginning of the game
 * CMC = TURN - a propability that player will be able to play card with converted mana cost equal to turn number
 * STREAK BOTH - an event when both events occurs every turn since beginning of the game