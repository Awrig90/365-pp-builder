# Affiliate Betslip Builder Chrome extension

A browser-only companion to the existing Streamlit affiliate URL builder.

The extension removes the manual DevTools/copy-paste step for supported bookmakers while preserving the same affiliate URL logic already used by the Streamlit app.

The Streamlit app remains in this repository as a separate fallback workflow.

## Supported bookmakers

### LiveScore Bet

**Workflow**

1. Open a LiveScore Bet fixture.
2. Add the desired same-event selections to the betslip.
3. Click **Affiliate Betslip Builder**.
4. Confirm the selections.
5. Choose the client profile.
6. Click **Copy affiliate URL**.

**How it works**

The extension reads `localStorage.selectionEntities` directly.

It:
- requires selections to belong to exactly one `eventId`;
- compares the stored event ID with the `SBTE_...` ID in the current fixture URL when present;
- rejects multi-event accumulators for this workflow;
- shows the detected selections before generating the link.

Current profile:
- Football News → `c_content_web_news_football`

### bet365

**Workflow**

1. Log in to bet365 normally if required.
2. Add selections to the betslip.
3. Click **Affiliate Betslip Builder**.
4. Confirm the detected selections/IDs.
5. Choose FST or RP.
6. Click **Copy affiliate URL**.

**How it works**

The extension reads `sessionStorage.betstring` directly, replacing the manual DevTools → Application → Session Storage workflow.

It deliberately mirrors the proven Python parser:
- `o` → odds
- `f` → market ID
- `fp` → selection ID

If the betstring contains a different `pv` value, the extension still uses `o` so generated links match the existing working Streamlit implementation.

Current profiles:
- FST → `365_624910`
- RP → `365_624911`

### Paddy Power

**Workflow**

1. Refresh Paddy Power after installing or reloading the extension.
2. Navigate to the fixture/competition.
3. Add selections normally.
4. Click **Affiliate Betslip Builder**.
5. Confirm the market/selection IDs.
6. Choose FST or Racing Post.
7. Click **Copy affiliate URL**.

**How it works**

Paddy Power exposes the required IDs in its live `implyBets` response rather than browser storage.

The extension installs a page-context listener at `document_start`, watches both `fetch` and XMLHttpRequest traffic for `implyBets`, finds `winRunnerOdds`, and stores the newest successful response as the current betslip snapshot.

This mirrors the previous manual workflow where the bottom-most `implyBets` entry in DevTools Network represents the latest betslip state.

Adding, removing or clearing selections causes a new snapshot to replace the previous one.

The extension does not alter Paddy Power requests or responses; it only reads a copy of the response.

Current profiles:
- FST → pid `17679402`, bid `7049`
- Racing Post → pid `17679403`, bid `7049`

## Pilot installation

For local/internal testing:

1. Download the repository/branch and extract it.
2. Open Chrome and go to `chrome://extensions`.
3. Enable **Developer mode**.
4. Click **Load unpacked**.
5. Select the `extension` folder.
6. Refresh any already-open bookmaker tabs once.

No build step is required.

If a managed work laptop blocks Developer mode or **Load unpacked**, do not try to bypass company policy. The extension will need to be distributed through an approved route such as the organisation's Chrome extension management or a Chrome Web Store deployment.

## Updating an unpacked test installation

After replacing the extension files:

1. Open `chrome://extensions`.
2. Click **Reload** on Affiliate Betslip Builder.
3. Refresh open bookmaker tabs.

For a completely clean test, remove the old unpacked extension and load the new `extension` folder again.

## Recommended acceptance test

Before wider rollout:

- LiveScore Bet: build a same-event bet builder, generate a link, and confirm the reconstructed betslip.
- bet365: build a betslip, generate both relevant client links where needed, and confirm the reconstructed selections.
- Paddy Power: add one selection, then two, remove one, and confirm the extension follows the latest state before generating a link.
- Repeat from a fresh browser session.
- Confirm the Streamlit fallback still produces the expected URLs.

## Files

- `manifest.json` — Manifest V3 extension configuration and supported bookmaker domains.
- `content.js` — reads LiveScore/bet365 browser storage and receives Paddy Power snapshots.
- `paddy-interceptor.js` — page-context listener for Paddy Power `implyBets` traffic.
- `popup.html`, `popup.css`, `popup.js` — extension UI, client selection and URL generation.

## Current status

LiveScore Bet, bet365 and Paddy Power have all been manually tested successfully using the unpacked extension.

The existing Streamlit app remains available and should not be retired until extension installation and operation have been proven on managed work laptops.
