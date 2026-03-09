"""Shared Streamlit UI and session-state logic for pizza recipe pages.

Each page passes its own *session_prefix* so multiple recipes can coexist in
the same Streamlit session without key collisions.  All session-state keys
used here are of the form ``f"{prefix}.{name}"``.
"""
from __future__ import annotations
from helpers import generate_print_button
from dough_class import Dough, Ingredients, Recipe

from pathlib import Path
import sys
from typing import Callable

import streamlit as st
from streamlit.delta_generator import DeltaGenerator

sys.path.insert(0, str(Path(__file__).parent))


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _k(prefix: str, name: str) -> str:
    """Build a namespaced session-state key."""
    return f"{prefix}.{name}"


def _ss(prefix: str, name: str):
    """Read a namespaced value from session state."""
    return st.session_state[_k(prefix, name)]


def _set(prefix: str, name: str, value) -> None:
    """Write a namespaced value to session state."""
    st.session_state[_k(prefix, name)] = value


# ---------------------------------------------------------------------------
# Recipe text
# ---------------------------------------------------------------------------

def generate_recipe_text(prefix: str, recipe: Recipe) -> str:
    """Build the markdown recipe string from current session state."""
    total_pizzas: float = _ss(prefix, "total_pizzas")
    weight_per_pizza: float = _ss(prefix, "weight_per_pizza")
    hydration: float = _ss(prefix, "hydration")

    stage_sections: list[str] = []
    for label, dough in recipe.stages.items():
        rows = "\n".join(
            f"- **{ing}**: {dough.get_ingredient_quantity(ing):.1f}"
            for ing in dough.ingredients_df.index
        )
        stage_sections.append(f"### {label.title()}\n{rows}")

    stages_text = "\n\n".join(stage_sections)

    return (
        f"# {recipe.name}\n\n"
        f"Generated with the [Pizza Dough Calculator App](https://pizzadoughcalculator.streamlit.app/).\n\n"
        f"Yields **{total_pizzas:.0f}** pizzas à **{weight_per_pizza:.1f} g**.\n\n"
        f"Hydration = **{hydration * 100:.0f} %**.\n\n"
        f"{stages_text}\n"
    )


# ---------------------------------------------------------------------------
# Session-state callbacks
# ---------------------------------------------------------------------------

def update_ingredients_table(prefix: str, recipe: Recipe) -> None:
    """Recompute all ingredient quantities after a control change."""
    ss = st.session_state
    key_ing: Ingredients = ss[_k(prefix, "key_ingredient")]
    ratio: float = ss[_k(prefix, "poulish_main_dough_ratio")]
    total_key_ing: float = ss[_k(prefix, "key_ingredient_input")]
    hydration: float = ss[_k(prefix, "hydration")]

    stage_list = list(recipe.stages.values())

    # Update hydration on the last stage (main dough)
    stage_list[-1].upgrade_ingredients_from_hydration(hydration)

    # Distribute the key ingredient across stages according to ratio
    n = len(stage_list)
    for i, dough in enumerate(stage_list):
        if key_ing not in dough.ingredients_df.index:
            continue
        # First stage gets `ratio` share; remaining stages split the rest evenly
        if i == 0:
            share = ratio
        else:
            share = (1.0 - ratio) / max(n - 1, 1)
        dough.scale_ingredient_new_quantity(key_ing, share * total_key_ing)

    usable = recipe.usable_weight()
    ss[_k(prefix, "total_pizzas")] = usable / \
        ss[_k(prefix, "weight_per_pizza")]


def _sync_slider_from_input(prefix: str, recipe: Recipe) -> None:
    key = _k(prefix, "key_ingredient_input")
    st.session_state[_k(prefix, "key_ingredient_slider")
                     ] = st.session_state[key]
    update_ingredients_table(prefix, recipe)


def _sync_input_from_slider(prefix: str, recipe: Recipe) -> None:
    key = _k(prefix, "key_ingredient_slider")
    st.session_state[_k(prefix, "key_ingredient_input")
                     ] = st.session_state[key]
    update_ingredients_table(prefix, recipe)


def view_key_ingredient_quantities(prefix: str, recipe: Recipe) -> None:
    """Refresh the key-ingredient input/slider to reflect current dough state."""
    key_ing: Ingredients = _ss(prefix, "key_ingredient")
    total = sum(
        d.get_ingredient_quantity(key_ing) for d in recipe.stages.values()
    )
    _set(prefix, "key_ingredient_input", total)
    _set(prefix, "key_ingredient_slider", total)


def update_total_pizza_amount(prefix: str, recipe: Recipe) -> None:
    """Scale all doughs when the pizza count or weight-per-pizza changes."""
    current_usable: float = _ss(prefix, "total_sum")
    new_amount = _ss(prefix, "total_pizzas") * _ss(prefix, "weight_per_pizza")
    factor = new_amount / current_usable
    for dough in recipe.stages.values():
        dough.scale_ingredients(factor)
    view_key_ingredient_quantities(prefix, recipe)


# ---------------------------------------------------------------------------
# Session initialisation & reset
# ---------------------------------------------------------------------------

def initialise_session(
    recipe: Recipe,
    prefix: str,
    init_flour: float,
    init_hydration: float,
    init_ratio: float,
    init_weight_per_pizza: float,
    default_stages_factory: Callable[[], dict[str, Dough]],
) -> None:
    """Populate session state on first run (idempotent)."""
    ss = st.session_state

    if _k(prefix, "stages_initialised") not in ss:
        fresh = default_stages_factory()
        recipe.stages.update(fresh)
        ss[_k(prefix, "stages_initialised")] = True

    defaults: dict[str, object] = {
        "total_pizzas": recipe.usable_weight() / init_weight_per_pizza,
        "weight_per_pizza": init_weight_per_pizza,
        "key_ingredient_input": init_flour,
        "poulish_main_dough_ratio": init_ratio,
        "hydration": init_hydration,
        "is_dry_yeast": False,
        "key_ingredient": Ingredients.FLOUR,
    }
    for name, value in defaults.items():
        if _k(prefix, name) not in ss:
            ss[_k(prefix, name)] = value

    ss[_k(prefix, "key_ingredient_slider")
       ] = ss[_k(prefix, "key_ingredient_input")]
    ss[_k(prefix, "total_sum")] = recipe.usable_weight()
    ss[_k(prefix, "recipe_text")] = generate_recipe_text(prefix, recipe)


def reset(
    recipe: Recipe,
    prefix: str,
    init_flour: float,
    init_hydration: float,
    init_ratio: float,
    init_weight_per_pizza: float,
    default_stages_factory: Callable[[], dict[str, Dough]],
) -> None:
    """Restore all defaults."""
    ss = st.session_state
    fresh = default_stages_factory()
    recipe.stages.update(fresh)

    ss[_k(prefix, "key_ingredient_input")] = init_flour
    ss[_k(prefix, "key_ingredient_slider")] = init_flour
    ss[_k(prefix, "hydration")] = init_hydration
    ss[_k(prefix, "poulish_main_dough_ratio")] = init_ratio
    ss[_k(prefix, "key_ingredient")] = Ingredients.FLOUR

    update_ingredients_table(prefix, recipe)

    ss[_k(prefix, "total_pizzas")] = recipe.usable_weight() / \
        init_weight_per_pizza
    ss[_k(prefix, "weight_per_pizza")] = init_weight_per_pizza


# ---------------------------------------------------------------------------
# UI components
# ---------------------------------------------------------------------------

def render_base_settings(
    expander: DeltaGenerator,
    prefix: str,
    recipe: Recipe,
) -> None:
    with expander:
        col1, col2 = st.columns(2)

        key_ing_key = _k(prefix, "key_ingredient")
        key_input_key = _k(prefix, "key_ingredient_input")
        key_slider_key = _k(prefix, "key_ingredient_slider")
        total_pizzas_key = _k(prefix, "total_pizzas")
        weight_key = _k(prefix, "weight_per_pizza")

        with col1:
            st.selectbox(
                "Select an ingredient to set the proportions of the recipe.",
                [Ingredients.FLOUR, Ingredients.WATER],
                key=key_ing_key,
                on_change=lambda: view_key_ingredient_quantities(
                    prefix, recipe),
            )
            key_ing_label = st.session_state[key_ing_key]
            st.write(f"How much {key_ing_label.lower()} are you going to use?")
            st.number_input(
                f"{key_ing_label}",
                key=key_input_key,
                min_value=0.0,
                max_value=10_000.0,
                step=100.0,
                on_change=lambda: _sync_slider_from_input(prefix, recipe),
            )
            st.slider(
                f"{key_ing_label}",
                key=key_slider_key,
                min_value=0.0,
                max_value=10_000.0,
                step=50.0,
                on_change=lambda: _sync_input_from_slider(prefix, recipe),
            )

        with col2:
            st.number_input(
                "Total amount of pizzas [-]",
                min_value=1.0,
                key=total_pizzas_key,
                step=1.0,
                on_change=lambda: update_total_pizza_amount(prefix, recipe),
            )
            st.number_input(
                "Weight per pizza [g]",
                min_value=1.0,
                key=weight_key,
                step=10.0,
                on_change=lambda: update_total_pizza_amount(prefix, recipe),
            )
            total_sum: float = st.session_state[_k(prefix, "total_sum")]
            weight: float = st.session_state[weight_key]
            st.write(f"Total weight is ca. {total_sum:,.2f} g.")
            st.write(
                f"Total weight results in ca. {total_sum / weight:.0f}"
                f" Pizzas à {weight} g."
            )


def render_advanced_settings(
    expander: DeltaGenerator,
    prefix: str,
    recipe: Recipe,
    extra_controls: Callable[[], None] | None = None,
) -> None:
    """Render the Advanced Settings expander.

    Parameters
    ----------
    extra_controls:
        Optional callable that renders recipe-specific controls (e.g. the
        dry-yeast toggle on the poulish page).  Called inside the expander
        after the standard sliders.
    """
    with expander:
        st.slider(
            "Poulish - Main Dough Ratio [%]",
            key=_k(prefix, "poulish_main_dough_ratio"),
            min_value=0.0,
            max_value=1.0,
            on_change=lambda: update_ingredients_table(prefix, recipe),
            help="How much of the first stage relative to the rest.",
        )
        st.slider(
            "Hydration [%]",
            key=_k(prefix, "hydration"),
            min_value=0.0,
            max_value=1.0,
            on_change=lambda: update_ingredients_table(prefix, recipe),
            help=(
                "E.g. a hydration of 70% means that in the final dough "
                "the water-to-flour ratio is 70%."
            ),
        )
        if extra_controls is not None:
            extra_controls()


def render_ingredients(recipe: Recipe) -> None:
    """Render one dataframe per dough stage."""
    for label, dough in recipe.stages.items():
        st.dataframe(
            dough.ingredients_df,
            use_container_width=True,
            key=f"table_{label}",
        )


# ---------------------------------------------------------------------------
# Top-level page renderer
# ---------------------------------------------------------------------------

def render_page(
    recipe: Recipe,
    prefix: str,
    init_flour: float,
    init_hydration: float,
    init_ratio: float,
    init_weight_per_pizza: float,
    default_stages_factory: Callable[[], dict[str, Dough]],
    page_title: str,
    extra_advanced_controls: Callable[[], None] | None = None,
) -> None:
    """Render a complete recipe page.

    Call this from ``main()`` in each page file after ``st.set_page_config``.
    """
    initialise_session(
        recipe=recipe,
        prefix=prefix,
        init_flour=init_flour,
        init_hydration=init_hydration,
        init_ratio=init_ratio,
        init_weight_per_pizza=init_weight_per_pizza,
        default_stages_factory=default_stages_factory,
    )

    st.write(
        "[![Star](https://img.shields.io/github/stars/sito115/PizzaApp.svg"
        "?logo=github&style=social)](https://github.com/sito115/PizzaApp)"
    )
    st.image("data/Pizza.jpg", use_container_width=True)
    st.title(page_title)

    left_col, right_col = st.columns(2)
    left_col.button(
        "Reset",
        key=_k(prefix, "is_reset"),
        on_click=lambda: reset(
            recipe=recipe,
            prefix=prefix,
            init_flour=init_flour,
            init_hydration=init_hydration,
            init_ratio=init_ratio,
            init_weight_per_pizza=init_weight_per_pizza,
            default_stages_factory=default_stages_factory,
        ),
    )
    generate_print_button(
        right_col, st.session_state[_k(prefix, "recipe_text")])

    with st.expander("Recipe"):
        st.write(st.session_state[_k(prefix, "recipe_text")])

    render_base_settings(
        st.expander("Base Settings", expanded=True), prefix, recipe
    )
    render_advanced_settings(
        st.expander("Advanced Settings"),
        prefix,
        recipe,
        extra_controls=extra_advanced_controls,
    )

    with st.expander("Ingredients", expanded=True):
        render_ingredients(recipe)
