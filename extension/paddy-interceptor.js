(() => {
  "use strict";

  const MESSAGE_SOURCE = "affiliate-betslip-builder";
  const IMPLY_PATTERN = /implybets/i;

  function findWinRunnerOdds(value) {
    if (!value || typeof value !== "object") {
      return null;
    }

    if (Array.isArray(value.winRunnerOdds)) {
      return value.winRunnerOdds;
    }

    if (Array.isArray(value)) {
      for (const item of value) {
        const found = findWinRunnerOdds(item);
        if (found) {
          return found;
        }
      }
      return null;
    }

    for (const child of Object.values(value)) {
      const found = findWinRunnerOdds(child);
      if (found) {
        return found;
      }
    }

    return null;
  }

  function extractSelections(payload) {
    const winRunnerOdds = findWinRunnerOdds(payload);

    if (!winRunnerOdds) {
      return null;
    }

    const selections = [];
    const seen = new Set();

    for (const item of winRunnerOdds) {
      const runner = item?.runner;
      const marketId = runner?.marketId;
      const selectionId = runner?.selectionId;

      if (marketId == null || selectionId == null) {
        continue;
      }

      const market = String(marketId);
      const selection = String(selectionId);
      const key = `${market}|${selection}`;

      if (seen.has(key)) {
        continue;
      }

      seen.add(key);

      selections.push({
        marketId: market,
        selectionId: selection,
        name:
          runner?.name ||
          runner?.runnerName ||
          runner?.selectionName ||
          item?.name ||
          item?.runnerName ||
          `Selection ${selections.length + 1}`
      });
    }

    return selections;
  }

  function publishPayload(payload, requestUrl) {
    try {
      const selections = extractSelections(payload);

      if (selections === null) {
        return;
      }

      window.postMessage(
        {
          source: MESSAGE_SOURCE,
          type: "PADDY_IMPLY_STATE",
          payload: {
            selections,
            requestUrl: String(requestUrl || ""),
            capturedAt: Date.now()
          }
        },
        "*"
      );
    } catch (_error) {
      // Never let extension parsing interfere with the bookmaker page.
    }
  }

  async function inspectFetchResponse(response, requestUrl) {
    try {
      const clone = response.clone();
      const contentType = clone.headers.get("content-type") || "";

      if (contentType.includes("application/json")) {
        publishPayload(await clone.json(), requestUrl);
        return;
      }

      const text = await clone.text();

      if (!text) {
        return;
      }

      publishPayload(JSON.parse(text), requestUrl);
    } catch (_error) {
      // Ignore responses that cannot be cloned or parsed.
    }
  }

  if (typeof window.fetch === "function") {
    const originalFetch = window.fetch;

    window.fetch = function (...args) {
      const requestUrl =
        typeof args[0] === "string"
          ? args[0]
          : args[0]?.url || "";

      const promise = originalFetch.apply(this, args);

      if (IMPLY_PATTERN.test(String(requestUrl))) {
        promise
          .then((response) => inspectFetchResponse(response, requestUrl))
          .catch(() => {});
      }

      return promise;
    };
  }

  if (typeof window.XMLHttpRequest === "function") {
    const originalOpen = XMLHttpRequest.prototype.open;
    const originalSend = XMLHttpRequest.prototype.send;

    XMLHttpRequest.prototype.open = function (method, url, ...rest) {
      this.__affiliateBetslipBuilderUrl = String(url || "");
      return originalOpen.call(this, method, url, ...rest);
    };

    XMLHttpRequest.prototype.send = function (...args) {
      const requestUrl = this.__affiliateBetslipBuilderUrl || "";

      if (IMPLY_PATTERN.test(requestUrl)) {
        this.addEventListener(
          "loadend",
          () => {
            try {
              if (this.responseType === "json") {
                publishPayload(this.response, requestUrl);
                return;
              }

              if (this.responseType === "" || this.responseType === "text") {
                const text = this.responseText;

                if (text) {
                  publishPayload(JSON.parse(text), requestUrl);
                }
              }
            } catch (_error) {
              // Ignore responses that cannot be parsed.
            }
          },
          { once: true }
        );
      }

      return originalSend.apply(this, args);
    };
  }
})();
