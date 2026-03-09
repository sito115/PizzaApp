"""Sour dough (mother yeast) pizza page."""
from __future__ import annotations
from recipe_helpers import render_page
from dough_class import Dough, Ingredients, Recipe
import streamlit as st
import pandas as pd

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1]))


# ---------------------------------------------------------------------------
# Page constants
# ---------------------------------------------------------------------------

PAGE_TITLE = "Pizza Dough Calculator – Sour Dough"
PREFIX = "sour_dough_page"

INIT_FLOUR: float = 250.0 + 460.0
INIT_HYDRATION: float = 0.68
INIT_RATIO: float = 0.3          # mother-yeast stage share of total flour
INIT_WEIGHT_PER_PIZZA: float = 250.0


# ---------------------------------------------------------------------------
# Default dough factories
# ---------------------------------------------------------------------------

def _default_stages() -> dict[str, Dough]:
    mother_yeast = Dough(
        ingredients_df=pd.DataFrame(
            [250, 170, 250],
            columns=["Value"],
            index=[Ingredients.FLOUR, Ingredients.WATER,
                   Ingredients.MOTHER_YEAST],
        )
    )
    main = Dough(
        ingredients_df=pd.DataFrame(
            [460, 300, 10, 10],
            columns=["Value"],
            index=[Ingredients.FLOUR, Ingredients.WATER,
                   Ingredients.OLIVE_OIL, Ingredients.SALT],
        )
    )
    main.hydration = INIT_HYDRATION
    return {"mother yeast": mother_yeast, "main dough": main}


# ---------------------------------------------------------------------------
# Recipe
# The mother-yeast quantity itself is excluded from the usable pizza weight
# because it is a starter that gets replenished, not consumed.
# ---------------------------------------------------------------------------

_recipe = Recipe(
    name=PAGE_TITLE,
    stages=_default_stages(),
    excluded_ingredients=[Ingredients.MOTHER_YEAST],
)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    st.set_page_config(page_title=PAGE_TITLE, page_icon=":pizza:")
    render_page(
        recipe=_recipe,
        prefix=PREFIX,
        init_flour=INIT_FLOUR,
        init_hydration=INIT_HYDRATION,
        init_ratio=INIT_RATIO,
        init_weight_per_pizza=INIT_WEIGHT_PER_PIZZA,
        default_stages_factory=_default_stages,
        page_title=PAGE_TITLE,
        extra_advanced_controls=None,   # no recipe-specific controls needed
    )


if __name__ == "__main__":
    main()
