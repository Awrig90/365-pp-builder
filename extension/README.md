# Affiliate Betslip Builder Chrome extension

This branch contains a Manifest V3 Chrome extension that generates affiliate betslip URLs directly from supported bookmaker pages.

## Supported bookmakers

### LiveScore Bet

1. Open a LiveScore Bet fixture.
2. Add the desired same-event selections to the betslip.
3. Click the **Affiliate Betslip Builder** extension.
4. Confirm the selections shown.
5. Choose the client profile.
6. Click **Copy affiliate URL**.

The extension reads `localStorage.selectionEntities` directly.

Safety checks:

- selections must contain exactly one LiveScore Bet `eventId`;
- the stored event ID is compared with the `SBTE_...` ID in the current fixture URL when present;
- multi-event accumulators are rejected for this workflow.

Current profile:

- Football News → `c_content_web_news_football`

### bet365

1. Log in to bet365 normally if required.
2. Add the desired selections to the betslip.
3. Click the **Affiliate Betslip Builder** extension.
4. Confirm the market/selection IDs and odds found.
5. Choose FST or RP.
6. Click **Copy affiliate URL**.

The extension reads `sessionStorage.betstring` directly, removing the existing DevTools → Application → Session Storage copy/paste step.

It deliberately mirrors the proven Python parser:

- `o` → odds
- `f` → market ID
- `fp` → selection ID

Even when a betstring also contains a different `pv` value, the extension currently continues to use `o` so its generated links match the existing working application.

Current profiles:

- FST → `365_624910`
- RP → `365_624911`

## Install locally for testing

1. Check out/download this branch.
2. Open Chrome and go to `chrome://extensions`.
3. Enable **Developer mode**.
4. Click **Load unpacked**.
5. Select the `extension` folder.
6. If a supported bookmaker tab was already open, refresh it once after installing or reloading the extension.

No build step is required.

## Next step

Add Paddy Power support by capturing the latest successful `implyBets` response and reading its `winRunnerOdds` snapshot.

A manual-paste fallback can be retained later if it remains useful after automatic capture is proven reliable.
