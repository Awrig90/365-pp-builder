# Affiliate Betslip Builder Chrome extension — LiveScore Bet proof of concept

This branch contains a small Manifest V3 Chrome extension that proves the browser-only workflow before bet365 and Paddy Power support are added.

## Current V1 workflow

1. Open a LiveScore Bet fixture.
2. Add the desired same-event selections to the betslip.
3. Click the **Affiliate Betslip Builder** extension.
4. Confirm the selections shown.
5. Choose the client profile.
6. Click **Copy affiliate URL**.

The extension reads LiveScore Bet's `localStorage.selectionEntities` directly. It does not require DevTools or the separate extension currently used to enable right-clicking.

## Safety checks

The extension:

- requires the selected entries to contain exactly one LiveScore Bet `eventId`;
- compares that event ID with the `SBTE_...` ID in the current fixture URL when present;
- refuses to generate a link if multiple events are detected;
- shows the selections it found before generating the URL.

This intentionally treats the LiveScore workflow as a same-event / bet-builder workflow rather than trying to support a standard multi-match accumulator.

## Install locally for testing

1. Check out/download this branch.
2. Open Chrome and go to `chrome://extensions`.
3. Enable **Developer mode**.
4. Click **Load unpacked**.
5. Select the `extension` folder.
6. If a LiveScore Bet tab was already open, refresh it once after installing the extension.

No build step is required.

## Current client profile

LiveScore Bet currently includes:

- Football News → `c_content_web_news_football`

Additional client profiles can be added later.

## Next steps after this proof works

1. Add bet365 support by reading `sessionStorage.betstring`.
2. Verify whether the affiliate URL should use the `o` or `pv` price field when those differ.
3. Add Paddy Power support by capturing the latest successful `implyBets` response and reading `winRunnerOdds`.
4. Add a manual-paste fallback only if it remains useful once automatic capture is proven reliable.
