# Affiliate URL Builder

This repository currently contains two ways to generate bookmaker affiliate betslip URLs.

## 1. Existing Streamlit app

The Python/Streamlit workflow remains supported as the fallback implementation.

It accepts bookmaker-specific copied betslip data and generates affiliate links for:

- Paddy Power
- bet365
- LiveScore Bet

The Streamlit workflow is intentionally being retained while the browser extension is piloted on managed work laptops.

## 2. Chrome extension

The `extension/` folder contains a Manifest V3 Chrome extension that removes the manual DevTools/copy-paste step.

Current browser workflow:

**Build the betslip on the bookmaker site → click the extension → choose the client → copy the affiliate URL.**

Supported bookmakers:

- LiveScore Bet
- bet365
- Paddy Power

See [extension/README.md](extension/README.md) for installation, implementation details and acceptance testing.

## Rollout status

The extension has been manually tested successfully on all three bookmakers in an unpacked local installation.

It should remain a pilot until installation and behaviour have also been validated on company-managed Chrome/work laptops. The Streamlit app should remain available during that period.
