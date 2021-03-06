import logging
import time
import traceback
from datetime import datetime, timezone
from typing import Dict

from colorama import Fore

from gui.windows import (
    baseResults,
    information,
    notEnoughInformation,
    priceInformation,
)
from item.generator import *
from utils import config
from utils.config import MIN_RESULTS, PROJECT_URL
from utils.exceptions import InvalidAPIResponseException
from utils.web import (
    exchange_currency,
    fetch,
    get_poe_prices_info,
    open_exchange_site,
    open_trade_site,
    query_item,
)


def get_response(item):
    """Based on the item given, get the response from the API

    :param item: Item to get response for
    :return: Response from approriate API
    """
    json = item.get_json()
    unsupportedCurrency = [
        "Warlord's Exalted Orb",
        "Crusader's Exalted Orb",
        "Redeemer's Exalted Orb",
        "Hunter's Exalted Orb",
        "Awakener's Orb",
    ]

    if isinstance(item, Currency) and item.name not in unsupportedCurrency:
        response = exchange_currency(json, config.LEAGUE)
    else:
        response = query_item(json, config.LEAGUE)

    return response


def get_trade_data(item):
    """For the given item, find current listings and retrieve prices & times

    :param item: Item to process
    :return: dict of count and prices, length of prices
    """

    def pretty_currency(curr):
        currency = curr
        # TODO: Add more currency types
        if "mir" in currency:
            currency = "Mirror"
        elif "exa" in currency:
            currency = "Exalt"
        elif "chaos" in currency:
            currency = "Chaos"
        elif "alch" in currency:
            currency = "Alch"
        elif "alt" in currency:
            currency = "Alt"
        elif "fuse" in currency:
            currency = "Fuse"
        return currency

    trade_info = None

    response = get_response(item)
    if not response:
        return {}

    if len(response["result"]) > 0:
        trade_info = fetch(response, isinstance(item, Currency))

    if trade_info:
        prev_account_name = ""
        # Modify data to usable status.
        times = []
        prices = []
        for trade in trade_info:  # Stop price fixers
            if trade["listing"]["price"]:
                if trade["listing"]["account"]["name"] != prev_account_name:
                    price = (
                        str(trade["listing"]["price"]["amount"])
                        + " "
                        + pretty_currency(
                            trade["listing"]["price"]["currency"]
                        )
                    )
                    prices.append(price)
                    times.append(
                        datetime.strptime(
                            trade["listing"]["indexed"], "%Y-%m-%dT%H:%M:%SZ"
                        )
                    )
                prev_account_name = trade["listing"]["account"]["name"]

        merged = {}
        for i in range(len(prices)):
            if prices[i] in merged:
                merged[prices[i]].append(times[i].replace(tzinfo=timezone.utc))
            else:
                merged[prices[i]] = [times[i].replace(tzinfo=timezone.utc)]

        for key, value in merged.items():
            combined = 0
            count = 0
            for t in value:
                combined += t.timestamp()
                count += 1
            combined = combined / count
            merged[key] = [
                count,
                datetime.fromtimestamp(combined, tz=timezone.utc),
            ]

        return merged, len(prices)
    return {}, 0


def print_info(info):
    if info != "":
        logging.info(info)
        information.add_info(info)
        information.create_at_cursor_left()


def price_item(item):
    """Pricing utility. Tries to price items by searching the API

    :param item: The item to search
    """
    try:

        data, results = get_trade_data(item)

        info = ""
        logging.debug(item.text)
        if results <= 0:
            info += item.remove_duplicate_mods()
            data, results = get_trade_data(item)

        if results <= 0:
            try:
                if item.rarity == "unique":
                    item2 = item
                    item2.remove_all_mods()
                    logging.info(f"[!] Re-pricing {item2.name} without mods.")
                    logging.debug(item2.get_json())
                    data, results = get_trade_data(item)
            except AttributeError:
                pass

        if results < MIN_RESULTS:
            info += item.remove_bad_mods()

        offline = False
        if results <= 0:
            info += f"[!] Checking offline sellers\n"
            item.set_offline()
            offline = True
            data, results = get_trade_data(item)

        if data:
            item.print()
            print_info(info)

            print_text = "[$] Prices: "
            for price, values in data.items():
                print_text += (
                    f"{Fore.YELLOW}{price}{Fore.RESET} x {values[0]}, "
                )

            print_text = print_text[:-2]
            logging.info(print_text)
            if results < MIN_RESULTS:
                logging.info(
                    "[!] Not enough data to confidently price this item."
                )
            priceInformation.add_price_information(data, offline)
            priceInformation.create_at_cursor()

            return results

        else:
            info += "[!] No results on /trade, using ML!"
            print_info(info)
            item.print()
            price = get_poe_prices_info(item)

            txt = ""

            if "min" in price:
                txt = txt + "Min: [" + str(round(price["min"], 2)) + "] "
            if "max" in price:
                txt = txt + "Max: [" + str(round(price["max"], 2)) + "] "
            if "currency" in price:
                txt = txt + "[" + price["currency"] + "] "
            if "pred_confidence_score" in price:
                txt = (
                    txt
                    + "Confidence: "
                    + str(floor(price["pred_confidence_score"]))
                    + "% "
                )

            logging.info(txt)
            if price:
                notEnoughInformation.add_poe_info_price(price)
            notEnoughInformation.create_at_cursor()

            return 0

    except InvalidAPIResponseException:
        logging.info(
            f"{Fore.RED}================== LOOKUP FAILED, PLEASE READ INSTRUCTIONS BELOW =================={Fore.RESET}"
        )
        logging.info(
            f"[!] Failed to parse response from POE API. If this error occurs again please open an issue at {PROJECT_URL}issues with the info below"
        )
        logging.info(
            f"{Fore.GREEN}================== START ISSUE DATA =================={Fore.RESET}"
        )
        logging.info(f"{Fore.GREEN}Title:{Fore.RESET}")
        logging.info("Failed to query item from trade API.")
        logging.info(f"{Fore.GREEN}Body:{Fore.RESET}")
        logging.info(
            "Macro failed to lookup item from POE trade API. Here is the item in question."
        )
        logging.info("====== ITEM DATA=====")
        if isinstance(item, Item):
            logging.info(item)
        else:
            logging.info(text)
        logging.info(
            f"{Fore.GREEN}================== END ISSUE DATA =================={Fore.RESET}"
        )
        logging.info(
            f"{Fore.RED}================== LOOKUP FAILED, PLEASE READ INSTRUCTIONS ABOVE =================={Fore.RESET}"
        )

    except Exception:
        exception = traceback.format_exc()
        logging.info(
            f"{Fore.RED}================== LOOKUP FAILED, PLEASE READ INSTRUCTIONS BELOW =================={Fore.RESET}"
        )
        logging.info(
            f"[!] Something went horribly wrong. If this error occurs again please open an issue at {PROJECT_URL}issues with the info below"
        )
        logging.info(
            f"{Fore.GREEN}================== START ISSUE DATA =================={Fore.RESET}"
        )
        logging.info(f"{Fore.GREEN}Title:{Fore.RESET}")
        logging.info("Failed to query item from trade API.")
        logging.info(f"{Fore.GREEN}Body:{Fore.RESET}")
        logging.info("Here is the item in question.")
        logging.info("====== ITEM DATA=====")
        if isinstance(item, Item):
            logging.info(item.text)
        else:
            if isinstance(text, list):
                logging.info("\n".join(text))
            else:
                logging.info(text)
        logging.info("====== TRACEBACK =====")
        logging.info(exception)
        logging.info(
            f"{Fore.GREEN}================== END ISSUE DATA =================={Fore.RESET}"
        )
        logging.info(
            f"{Fore.RED}================== LOOKUP FAILED, PLEASE READ INSTRUCTIONS ABOVE =================={Fore.RESET}"
        )
