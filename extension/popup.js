(() => {
  "use strict";

  const PROFILES = {
    "LiveScore Bet": {
      "Football News": {
        btag: "c_content_web_news_football"
      }
    },
    "bet365": {
      "FST": {
        affiliate: "365_624910"
      },
      "RP": {
        affiliate: "365_624911"
      }
    }
  };

  let currentState = null;

  const bookmakerEl = document.getElementById("bookmaker");
  const statusEl = document.getElementById("status");
  const sectionEl = document.getElementById("betslip-section");
  const countEl = document.getElementById("selection-count");
  const eventIdEl = document.getElementById("event-id");
  const listEl = document.getElementById("selection-list");
  const clientSelectEl = document.getElementById("client-select");
  const copyButtonEl = document.getElementById("copy-button");
  const copyStatusEl = document.getElementById("copy-status");

  function setStatus(message, kind = "") {
    statusEl.textContent = message;
    statusEl.className = `status ${kind}`.trim();
  }

  function buildLiveScoreUrl(state, profile) {
    const selectionIds = state.selections.map((selection) => selection.selectionId);

    if (!selectionIds.length) {
      throw new Error("No LiveScore Bet selections were found.");
    }

    if (!state.eventId) {
      throw new Error("No LiveScore Bet event ID was found.");
    }

    return (
      "https://www.livescorebet.com/uk/dl/addtobetslip" +
      `?selectionIds=${selectionIds.join(",")}` +
      "&bettype=acca" +
      "&stake=10" +
      "&action=sev" +
      `&eventid=${state.eventId}` +
      `&btag=${profile.btag}`
    );
  }

  function buildBet365Url(state, profile) {
    if (!state.selections.length) {
      throw new Error("No bet365 selections were found.");
    }

    const betslipString = state.selections
      .map((selection) => `${selection.marketId}-${selection.selectionId}~${selection.odds}`)
      .join("|");

    return (
      "https://www.bet365.com/dl/sportsbookredirect" +
      `?affiliate=${profile.affiliate}` +
      `&bs=${betslipString}` +
      "&bet=1"
    );
  }

  function buildAffiliateUrl(state, profile) {
    if (state.bookmaker === "LiveScore Bet") {
      return buildLiveScoreUrl(state, profile);
    }

    if (state.bookmaker === "bet365") {
      return buildBet365Url(state, profile);
    }

    throw new Error("This bookmaker is not supported yet.");
  }

  function populateProfiles(bookmaker) {
    clientSelectEl.textContent = "";
    const profiles = PROFILES[bookmaker] || {};

    for (const name of Object.keys(profiles)) {
      const option = document.createElement("option");
      option.value = name;
      option.textContent = name;
      clientSelectEl.appendChild(option);
    }
  }

  function selectionMeta(state, selection) {
    const odds = selection.fractionalOdds || selection.odds || "";

    if (state.bookmaker === "bet365") {
      const ids = `market ${selection.marketId} · selection ${selection.selectionId}`;
      return odds ? `${odds} · ${ids}` : ids;
    }

    return odds ? `${odds} · ${selection.selectionId}` : selection.selectionId;
  }

  function renderState(state) {
    currentState = state;
    bookmakerEl.textContent = state.bookmaker || "Unsupported bookmaker";

    if (!state.ok) {
      setStatus(state.message || "Could not read this betslip.", "error");
      sectionEl.hidden = true;
      return;
    }

    setStatus("Betslip detected.", "success");
    sectionEl.hidden = false;

    countEl.textContent = `${state.selections.length} selection${state.selections.length === 1 ? "" : "s"}`;
    eventIdEl.textContent = state.eventId || "";

    listEl.textContent = "";

    for (const selection of state.selections) {
      const item = document.createElement("li");

      const name = document.createElement("span");
      name.className = "selection-name";
      name.textContent = selection.name;

      const meta = document.createElement("span");
      meta.className = "selection-meta";
      meta.textContent = selectionMeta(state, selection);

      item.appendChild(name);
      item.appendChild(meta);

      if (selection.suspended) {
        const warning = document.createElement("span");
        warning.className = "selection-meta selection-warning";
        warning.textContent = "Suspended";
        item.appendChild(warning);
      }

      listEl.appendChild(item);
    }

    populateProfiles(state.bookmaker);
    copyButtonEl.disabled = clientSelectEl.options.length === 0;
  }

  async function loadBetslip() {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

    if (!tab?.id || !tab.url) {
      setStatus("Could not determine the active tab.", "error");
      return;
    }

    const supported =
      tab.url.startsWith("https://www.livescorebet.com/") ||
      tab.url.startsWith("https://livescorebet.com/") ||
      tab.url.startsWith("https://www.bet365.com/") ||
      tab.url.startsWith("https://bet365.com/");

    if (!supported) {
      bookmakerEl.textContent = "Unsupported page";
      setStatus("This page is not supported yet.", "error");
      return;
    }

    try {
      const state = await chrome.tabs.sendMessage(tab.id, { type: "GET_BETSLIP_STATE" });
      renderState(state);
    } catch (error) {
      setStatus(
        "Could not read the page. If you installed or reloaded the extension while this tab was already open, refresh the bookmaker page once and try again.",
        "error"
      );
    }
  }

  copyButtonEl.addEventListener("click", async () => {
    copyStatusEl.textContent = "";
    copyStatusEl.className = "copy-status";

    if (!currentState?.ok) {
      copyStatusEl.textContent = "No valid betslip is available.";
      return;
    }

    const bookmakerProfiles = PROFILES[currentState.bookmaker] || {};
    const profile = bookmakerProfiles[clientSelectEl.value];

    if (!profile) {
      copyStatusEl.textContent = "Choose a valid client.";
      return;
    }

    try {
      const url = buildAffiliateUrl(currentState, profile);
      await navigator.clipboard.writeText(url);
      copyStatusEl.textContent = "Affiliate URL copied.";
      copyStatusEl.className = "copy-status success";
    } catch (error) {
      copyStatusEl.textContent = error.message;
    }
  });

  loadBetslip();
})();
