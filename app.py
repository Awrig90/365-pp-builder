
import streamlit as st

from bookmakers import build_url_for_bookmaker
from config import AFFILIATE_PROFILES, BOOKMAKERS


def display_extracted_selections(bookmaker: str, extracted_selections):
    """
    Display extracted selections in a readable way.

    Paddy Power selections:
        market_id, selection_id

    bet365 selections:
        market_id, selection_id, odds
    """

    st.subheader("Extracted selections")

    for index, selection in enumerate(extracted_selections, start=1):
        if bookmaker == "Paddy Power":
            market_id, selection_id = selection

            st.write(
                f"**Selection {index}:** marketId `{market_id}` / selectionId `{selection_id}`"
            )

        elif bookmaker == "bet365":
            market_id, selection_id, odds = selection

            st.write(
                f"**Selection {index}:** marketId `{market_id}` / "
                f"selectionId `{selection_id}` / odds `{odds}`"
            )

        else:
            st.write(f"**Selection {index}:** `{selection}`")


def main():
    st.set_page_config(
        page_title="Affiliate URL Builder",
        page_icon="🔗",
        layout="centered",
    )

    st.title("Affiliate URL Builder")

    st.write(
        "Select a bookmaker, choose an affiliate profile, paste the copied betslip/string, "
        "and generate the affiliate URL."
    )

    bookmaker = st.selectbox(
        "Bookmaker",
        options=BOOKMAKERS,
    )

    affiliate_options = list(AFFILIATE_PROFILES[bookmaker].keys())

    affiliate_name = st.selectbox(
        "Affiliate profile",
        options=affiliate_options,
    )

    selected_affiliate_profile = AFFILIATE_PROFILES[bookmaker][affiliate_name]

    raw_input = st.text_area(
        f"{bookmaker} pasted string",
        height=250,
        placeholder="Paste copied betslip/string here...",
    )

    generate_clicked = st.button("Generate URL", type="primary")

    if generate_clicked:
        if not raw_input.strip():
            st.error("Paste a betslip/string first.")
            return

        try:
            final_url, extracted_selections = build_url_for_bookmaker(
                bookmaker=bookmaker,
                raw_text=raw_input,
                affiliate_profile=selected_affiliate_profile,
            )

        except ValueError as error:
            st.error(str(error))
            return

        st.success(f"Generated URL with {len(extracted_selections)} selection(s).")

        display_extracted_selections(bookmaker, extracted_selections)

        st.subheader("Generated affiliate URL")

        st.text_input(
            "Copy this URL",
            value=final_url,
        )

        st.code(final_url, language="text")


if __name__ == "__main__":
    main()
