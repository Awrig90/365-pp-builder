
import re
from typing import Callable, Dict, List, Tuple


AffiliateProfile = Dict[str, str]

# Paddy returns:
#   market_id, selection_id
PaddyLeg = Tuple[str, str]

# bet365 returns:
#   market_id, selection_id, odds
Bet365Leg = Tuple[str, str, str]

# LiveScore Bet returns:
#   selection_ids, event_id
LiveScoreBetData = Tuple[List[str], str]

Selection = Tuple[str, ...]


# -----------------------------
# Helper functions
# -----------------------------

def dedupe_preserve_order(items: List[str]) -> List[str]:
    """
    Remove duplicates while preserving the original order.
    """

    seen = set()
    result = []

    for item in items:
        if item not in seen:
            result.append(item)
            seen.add(item)

    return result


def normalise_escaped_underscores(text: str) -> str:
    """
    Some copied examples may contain escaped underscores, like:
        SBTS\\_2\\_4316937379

    This converts them back to:
        SBTS_2_4316937379
    """

    return text.replace("\\_", "_")


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
# LiveScore Bet
# -----------------------------

def extract_livescore_bet_data(raw_text: str) -> LiveScoreBetData:
    """
    Extract LiveScore Bet selection IDs and event ID.

    Selection IDs look like:
        SBTS_2_4316937379

    Event IDs look like:
        SBTE_2_1028142651

    The event ID is usually found inside the event URL.
    """

    cleaned_text = normalise_escaped_underscores(raw_text)

    selection_pattern = r"SBTS_\d+_\d+"
    event_pattern = r"SBTE_\d+_\d+"

    selection_ids = re.findall(selection_pattern, cleaned_text)
    event_ids = re.findall(event_pattern, cleaned_text)

    selection_ids = dedupe_preserve_order(selection_ids)
    event_ids = dedupe_preserve_order(event_ids)

    if not selection_ids:
        raise ValueError(
            "No LiveScore Bet selection IDs found. Expected codes like SBTS_2_4316937379."
        )

    if not event_ids:
        raise ValueError(
            "No LiveScore Bet event ID found. Paste the event URL containing a code like SBTE_2_1028142651."
        )

    if len(event_ids) > 1:
        raise ValueError(
            "Multiple LiveScore Bet event IDs found. Paste only one match/event URL."
        )

    return selection_ids, event_ids[0]


def build_livescore_bet_url(
    profile: AffiliateProfile,
    livescore_data: LiveScoreBetData,
) -> str:
    """
    Build a LiveScore Bet affiliate URL.

    Expected format:
        https://www.livescorebet.com/uk/dl/addtobetslip?selectionIds=SBTS_...,...&bettype=acca&stake=10&action=sev&eventid=SBTE_...&btag=...
    """

    selection_ids, event_id = livescore_data

    if not selection_ids:
        raise ValueError("No LiveScore Bet selection IDs were provided.")

    if not event_id:
        raise ValueError("No LiveScore Bet event ID was provided.")

    btag = profile["btag"]

    selection_ids_string = ",".join(selection_ids)

    final_url = (
        "https://www.livescorebet.com/uk/dl/addtobetslip"
        f"?selectionIds={selection_ids_string}"
        f"&bettype=acca"
        f"&stake=10"
        f"&action=sev"
        f"&eventid={event_id}"
        f"&btag={btag}"
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
    "LiveScore Bet": {
        "extract": extract_livescore_bet_data,
        "build": build_livescore_bet_url,
    },
}


def build_url_for_bookmaker(
    bookmaker: str,
    raw_text: str,
    affiliate_profile: AffiliateProfile,
):
    """
    Generic bookmaker dispatcher.

    The Streamlit app calls this function and does not need to know the details
    of each bookmaker's URL format.
    """

    if bookmaker not in BOOKMAKER_FUNCTIONS:
        raise ValueError(f"Unsupported bookmaker: {bookmaker}")

    extractor = BOOKMAKER_FUNCTIONS[bookmaker]["extract"]
    builder = BOOKMAKER_FUNCTIONS[bookmaker]["build"]

    extracted_data = extractor(raw_text)

    if not extracted_data:
        raise ValueError(
            f"No valid selections found for {bookmaker}. "
            "Check that you pasted the correct betslip/string format."
        )

    final_url = builder(affiliate_profile, extracted_data)

    return final_url, extracted_data
