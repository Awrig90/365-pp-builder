
import re
from typing import Callable, Dict, List, Tuple


AffiliateProfile = Dict[str, str]

# Paddy returns:
#   market_id, selection_id
PaddyLeg = Tuple[str, str]

# bet365 returns:
#   market_id, selection_id, odds
Bet365Leg = Tuple[str, str, str]

Selection = Tuple[str, ...]


# -----------------------------
# Paddy Power
# -----------------------------

def extract_paddy_power_legs(raw_text: str) -> List[PaddyLeg]:
    """
    Extract Paddy Power market IDs and selection IDs from pasted betslip text.

    Example:
        {runner: {marketId: "927.358980525", selectionId: 37944}, ...}

    Returns:
        [
            ("927.358980525", "37944"),
            ...
        ]
    """

    pattern = r'marketId:\s*"([^"]+)"\s*,\s*selectionId:\s*"?(\d+)"?'
    return re.findall(pattern, raw_text)


def build_paddy_power_url(profile: AffiliateProfile, legs: List[PaddyLeg]) -> str:
    """
    Build a Paddy Power affiliate URL.

    Multiple legs are joined using encoded:
        %26leg%3D

    Each leg ends with:
        %7CSIMPLE_SELECTION%7C
    """

    if not legs:
        raise ValueError("No Paddy Power legs were provided.")

    pid = profile["pid"]
    bid = profile["bid"]

    encoded_leg_parts = []

    for market_id, selection_id in legs:
        encoded_leg = f"{market_id}%7C{selection_id}%7CSIMPLE_SELECTION%7C"
        encoded_leg_parts.append(encoded_leg)

    encoded_legs = "%26leg%3D".join(encoded_leg_parts)

    final_url = (
        "https://media.paddypower.com/redirect.aspx"
        f"?pid={pid}"
        f"&bid={bid}"
        f"&redirectURL=https://www.paddypower.com/bet?action=addLegs&leg={encoded_legs}"
    )

    return final_url


# -----------------------------
# bet365
# -----------------------------

def extract_bet365_legs(raw_text: str) -> List[Bet365Leg]:
    """
    Extract bet365 market IDs, selection IDs, and odds from copied betslip text.

    Example input section:
        #o=10/11#pv=10/11#f=185820809#fp=101630302#

    Required output:
        [
            ("185820809", "101630302", "10/11"),
            ...
        ]
    """

    pattern = r"#o=([^#]+)#.*?#f=(\d+)#fp=(\d+)"

    matches = re.findall(pattern, raw_text, flags=re.DOTALL)

    legs = []

    for odds, market_id, selection_id in matches:
        legs.append((market_id, selection_id, odds))

    return legs


def build_bet365_url(profile: AffiliateProfile, legs: List[Bet365Leg]) -> str:
    """
    Build a bet365 affiliate URL.

    Expected format:
        https://www.bet365.com/dl/sportsbookredirect?affiliate=AFFILIATE&bs=MARKET-SELECTION~ODDS|MARKET-SELECTION~ODDS&bet=1
    """

    if not legs:
        raise ValueError("No bet365 legs were provided.")

    affiliate = profile["affiliate"]

    betslip_parts = []

    for market_id, selection_id, odds in legs:
        betslip_part = f"{market_id}-{selection_id}~{odds}"
        betslip_parts.append(betslip_part)

    betslip_string = "|".join(betslip_parts)

    final_url = (
        "https://www.bet365.com/dl/sportsbookredirect"
        f"?affiliate={affiliate}"
        f"&bs={betslip_string}"
        f"&bet=1"
    )

    return final_url


# -----------------------------
# Bookmaker registry
# -----------------------------

BOOKMAKER_FUNCTIONS: Dict[str, Dict[str, Callable]] = {
    "Paddy Power": {
        "extract": extract_paddy_power_legs,
        "build": build_paddy_power_url,
    },
    "bet365": {
        "extract": extract_bet365_legs,
        "build": build_bet365_url,
    },
}


def build_url_for_bookmaker(
    bookmaker: str,
    raw_text: str,
    affiliate_profile: AffiliateProfile,
) -> Tuple[str, List[Selection]]:
    """
    Generic bookmaker dispatcher.

    The Streamlit app calls this function and does not need to know the details
    of each bookmaker's URL format.
    """

    if bookmaker not in BOOKMAKER_FUNCTIONS:
        raise ValueError(f"Unsupported bookmaker: {bookmaker}")

    extractor = BOOKMAKER_FUNCTIONS[bookmaker]["extract"]
    builder = BOOKMAKER_FUNCTIONS[bookmaker]["build"]

    selections = extractor(raw_text)

    if not selections:
        raise ValueError(
            f"No valid selections found for {bookmaker}. "
            "Check that you pasted the correct betslip/string format."
        )

    final_url = builder(affiliate_profile, selections)

    return final_url, selections
