from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

import numpy as np
import pandas as pd


class Ingredients(StrEnum):
    FLOUR = "Flour [g]"
    WATER = "Water [mL]"
    FRESH_YEAST = "Fresh Yeast [g]"
    DRY_YEAST = "Dry Yeast [g]"
    SALT = "Salt [g]"
    HONEY = "Honey [g]"
    OLIVE_OIL = "Olive Oil [g]"
    MOTHER_YEAST = "Mother Yeast [g]"


@dataclass
class Dough:
    """Represents a pizza dough component with its ingredient quantities."""

    ingredients_df: pd.DataFrame
    _hydration: float = field(default=np.nan, repr=False)

    def __post_init__(self) -> None:
        self.ingredients_df["Value"] = pd.to_numeric(
            self.ingredients_df["Value"], errors="coerce"
        )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def hydration(self) -> float:
        return self._hydration

    @hydration.setter
    def hydration(self, value: float) -> None:
        if 0.0 < value <= 1.0:
            self._hydration = value
        else:
            raise ValueError(f"Hydration must be in ]0, 1], got {value!r}.")

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def total_sum(self) -> float:
        """Return the total weight of all ingredients."""
        return float(self.ingredients_df["Value"].sum())

    def get_ingredient_quantity(self, key: Ingredients) -> float:
        """Return the quantity of *key*, or 0.0 if not present."""
        if key not in self.ingredients_df.index:
            return 0.0
        value = pd.to_numeric(
            self.ingredients_df.loc[key, "Value"], errors="coerce")
        # type: ignore[arg-type]
        return float(value) if not pd.isna(value) else 0.0

    # ------------------------------------------------------------------
    # Mutations
    # ------------------------------------------------------------------

    def scale_ingredients(self, scale_factor: float) -> None:
        """Multiply all ingredient quantities by *scale_factor*."""
        if scale_factor <= 0:
            return
        self.ingredients_df["Value"] *= scale_factor

    def scale_ingredient_new_quantity(self, key: Ingredients, new_quantity: float) -> None:
        """Scale all ingredients so that *key* reaches *new_quantity*."""
        if key not in self.ingredients_df.index:
            raise KeyError(f"{key!r} not found in ingredients.")
        old_quantity = self.get_ingredient_quantity(key)
        if old_quantity == 0.0:
            raise ValueError(f"Cannot scale from a zero quantity for {key!r}.")
        self.scale_ingredients(new_quantity / old_quantity)

    def upgrade_ingredients_from_hydration(self, new_hydration: float) -> None:
        """Adjust the water quantity to match *new_hydration*.

        If *new_hydration* equals the current hydration, this is a no-op.
        """
        if new_hydration == self._hydration:
            return
        old_hydration = self._hydration
        self.hydration = new_hydration  # validated via setter
        scale_factor = self._hydration / old_hydration
        raw = self.ingredients_df.loc[Ingredients.WATER, "Value"]
        value = pd.to_numeric(raw, errors="coerce")
        if pd.isna(value):  # type: ignore[arg-type]
            raise ValueError(f"Invalid value for WATER: {raw!r}")
        self.ingredients_df.loc[Ingredients.WATER, "Value"] = float(
            value) * scale_factor  # type: ignore[arg-type]


@dataclass
class Recipe:
    """A named collection of dough stages that together make up a pizza recipe.

    Parameters
    ----------
    name:
        Human-readable recipe name shown in the UI.
    stages:
        Ordered mapping of stage label → Dough.  The labels are used as
        session-state keys and as table headings.
    excluded_ingredients:
        Ingredients that should *not* count toward the usable pizza weight
        (e.g. the mother-yeast starter that is replenished, not consumed).
    """

    name: str
    stages: dict[str, Dough]
    excluded_ingredients: list[Ingredients] = field(default_factory=list)

    def usable_weight(self) -> float:
        """Total dough weight minus any excluded ingredients."""
        total = sum(d.total_sum() for d in self.stages.values())
        excluded = sum(
            d.get_ingredient_quantity(ing)
            for d in self.stages.values()
            for ing in self.excluded_ingredients
        )
        return total - excluded
