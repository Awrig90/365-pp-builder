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

It mirrors the proven Python parser:

- `o` → odds
- `f` → market ID
- `fp` → selection ID

Current profiles:

- FST → `365_624910`
- RP → `365_624911`

### Paddy Power

Paddy Power works differently because the required IDs are returned in the site's live `implyBets` response rather than being stored in browser storage.

1. After installing/reloading this extension, refresh the Paddy Power page once.
2. Navigate to the fixture/competition where you want to build the betslip.
3. Add selections normally.
4. Click the **Affiliate Betslip Builder** extension.
5. Confirm the market/selection IDs found.
6. Choose FST or Racing Post.
7. Click **Copy affiliate URL**.

The extension installs a page-context listener at `document_start`. It watches both `fetch` and XMLHttpRequest traffic for `implyBets`, parses the returned JSON, finds `winRunnerOdds`, and treats every successful response as a complete snapshot of the current betslip.

That mirrors the existing manual workflow where the bottom-most `implyBets` entry in DevTools Network is always the latest betslip state.

If selections are removed or the betslip is cleared, the next `implyBets` response replaces the previously captured state.

The page's network requests and responses are not modified; the extension only reads a cloned/copy of the response.

Current profiles:

- FST → pid `17679402`, bid `7049`
- Racing Post → pid `17679403`, bid `7049`

## Install locally for testing

1. Check out/download this branch.
2. Open Chrome and go to `chrome://extensions`.
3. Enable **Developer mode**.
4. Click **Load unpacked**.
5. Select the `extension` folder.
6. Click **Reload** on the extension after updating files.
7. Refresh any already-open bookmaker tabs once.

No build step is required.

## Testing Paddy Power

Paddy Power must be refreshed after installing or reloading the extension because the network listener has to exist before the relevant `implyBets` response occurs.

For a first test:

1. Reload the extension in `chrome://extensions`.
2. Refresh the Paddy Power fixture page.
3. Start with an empty betslip if convenient.
4. Add one selection.
5. Open the extension and confirm one selection is detected.
6. Add another selection and confirm the extension now shows two.
7. Remove one selection and confirm the next captured state reflects the removal.
8. Generate the affiliate URL and open it to confirm Paddy reconstructs the intended betslip.

LiveScore Bet and bet365 should continue to work unchanged.
