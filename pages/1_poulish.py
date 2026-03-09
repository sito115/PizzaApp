"""Poulish pizza dough page."""
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

PAGE_TITLE = "Pizza Dough Calculator – Poulish"
PREFIX = "poulish_page"

INIT_FLOUR: float = 1_000.0
INIT_HYDRATION: float = 0.7
INIT_RATIO: float = 0.3          # poulish share of total flour
INIT_WEIGHT_PER_PIZZA: float = 250.0


# ---------------------------------------------------------------------------
# Default dough factories
# ---------------------------------------------------------------------------

def _default_stages() -> dict[str, Dough]:
    poulish = Dough(
        ingredients_df=pd.DataFrame(
            [300, 300, 5, 5],
            columns=["Value"],
            index=[Ingredients.FLOUR, Ingredients.WATER,
                   Ingredients.FRESH_YEAST, Ingredients.HONEY],
        )
    )
    main = Dough(
        ingredients_df=pd.DataFrame(
            [700, 400, 10, 25],
            columns=["Value"],
            index=[Ingredients.FLOUR, Ingredients.WATER,
                   Ingredients.OLIVE_OIL, Ingredients.SALT],
        )
    )
    main.hydration = INIT_HYDRATION
    return {"poulish": poulish, "main dough": main}


# ---------------------------------------------------------------------------
# Recipe
# ---------------------------------------------------------------------------

_recipe = Recipe(name=PAGE_TITLE, stages=_default_stages())


# ---------------------------------------------------------------------------
# Recipe-specific controls
# ---------------------------------------------------------------------------

def _change_yeast() -> None:
    poulish: Dough = _recipe.stages["poulish"]
    if st.session_state[f"{PREFIX}.is_dry_yeast"]:
        poulish.ingredients_df.loc[Ingredients.FRESH_YEAST, "Value"] *= 0.5
        poulish.ingredients_df.rename(
            index={Ingredients.FRESH_YEAST: Ingredients.DRY_YEAST}, inplace=True
        )
    else:
        poulish.ingredients_df.loc[Ingredients.DRY_YEAST, "Value"] *= 2
        poulish.ingredients_df.rename(
            index={Ingredients.DRY_YEAST: Ingredients.FRESH_YEAST}, inplace=True
        )


def _extra_controls() -> None:
    st.checkbox(
        "Dry yeast",
        value=False,
        key=f"{PREFIX}.is_dry_yeast",
        on_change=_change_yeast,
        help="Dry yeast requires roughly half the amount of fresh yeast.",
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
        extra_advanced_controls=_extra_controls,
    )


if __name__ == "__main__":
    main()
