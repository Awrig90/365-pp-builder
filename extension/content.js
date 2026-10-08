(() => {
  "use strict";

  const BOOKMAKER = "LiveScore Bet";
  const SELECTIONS_KEY = "selectionEntities";

  function eventIdFromUrl(url) {
    const match = String(url || "").match(/SBTE_\d+_\d+/);
    return match ? match[0] : null;
  }

  function readLiveScoreBetslip() {
    let raw;

    try {
      raw = window.localStorage.getItem(SELECTIONS_KEY);
    } catch (error) {
      return {
        ok: false,
        bookmaker: BOOKMAKER,
        code: "STORAGE_UNAVAILABLE",
        message: `Could not read LiveScore Bet local storage: ${error.message}`
      };
    }

    if (!raw) {
      return {
        ok: false,
        bookmaker: BOOKMAKER,
        code: "NO_BETSLIP",
        message: "No LiveScore Bet selections were found. Add selections to the betslip first."
      };
    }

    let entities;

    try {
      entities = JSON.parse(raw);
    } catch (error) {
      return {
        ok: false,
        bookmaker: BOOKMAKER,
        code: "INVALID_STORAGE",
        message: `LiveScore Bet selectionEntities is not valid JSON: ${error.message}`
      };
    }

    if (!entities || typeof entities !== "object" || Array.isArray(entities)) {
      return {
        ok: false,
        bookmaker: BOOKMAKER,
        code: "INVALID_STORAGE",
        message: "LiveScore Bet selectionEntities has an unexpected format."
      };
    }

    const selections = Object.values(entities)
      .filter((item) => item && typeof item === "object" && item.selectionId)
      .map((item) => ({
        selectionId: String(item.selectionId),
        eventId: item.eventId ? String(item.eventId) : null,
        marketId: item.marketId ? String(item.marketId) : null,
        name: item.name || item.shortName || String(item.selectionId),
        shortName: item.shortName || item.name || String(item.selectionId),
        odds: item.odds ?? null,
        fractionalOdds: item.displayOdds?.fractional ?? null,
        suspended: Boolean(item.suspended)
      }));

    if (!selections.length) {
      return {
        ok: false,
        bookmaker: BOOKMAKER,
        code: "NO_BETSLIP",
        message: "selectionEntities was present, but no selections could be read from it."
      };
    }

    const eventIds = [...new Set(selections.map((selection) => selection.eventId).filter(Boolean))];

    if (eventIds.length !== 1) {
      return {
        ok: false,
        bookmaker: BOOKMAKER,
        code: "MULTI_EVENT",
        message:
          eventIds.length > 1
            ? "Multiple fixtures were detected. This LiveScore Bet link workflow currently supports same-event bet builders only."
            : "The selected entries do not contain a usable LiveScore Bet event ID.",
        selections
      };
    }

    const eventId = eventIds[0];
    const pageEventId = eventIdFromUrl(window.location.href);

    if (pageEventId && pageEventId !== eventId) {
      return {
        ok: false,
        bookmaker: BOOKMAKER,
        code: "EVENT_MISMATCH",
        message: `The current page is ${pageEventId}, but the stored betslip selections belong to ${eventId}. Clear or rebuild the betslip before generating a link.`,
        eventId,
        pageEventId,
        selections
      };
    }

    return {
      ok: true,
      bookmaker: BOOKMAKER,
      eventId,
      pageEventId,
      selections
    };
  }

  chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
    if (message?.type !== "GET_BETSLIP_STATE") {
      return false;
    }

    sendResponse(readLiveScoreBetslip());
    return false;
  });
})();
