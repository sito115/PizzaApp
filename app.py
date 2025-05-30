# A basic streamlit app which takes user input for pizza dough creation and spits out a recipe.

import streamlit as st

pages = [
    st.Page("pages/1_poulish.py", title="Double Fermented Pizza Dough", default=True),
    # st.Page("pages/2_sour_dough.py", title="Sour Dough Pizza Dough"),
]


pg = st.navigation(pages)
pg.run()