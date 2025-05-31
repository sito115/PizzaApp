from enum import StrEnum
import numpy as np
from dataclasses import dataclass
import pandas as pd

class Ingredients(StrEnum):
    FLOUR  = 'Flour [g]'
    WATER  = 'Water [mL]'
    FRESH_YEAST  = 'Fresh Yeast [g]'
    DRY_YEAST  = 'Dry Yeast [g]'
    SALT   = 'Salt [g]'
    HONEY  = 'Honey [g]'
    OLIVE_OIL = 'Olive Oil [g]'
    MOTHER_YEAST = 'Mother Yeast [g]'


@dataclass
class Dough():
    ingredients_df: pd.DataFrame
    _hydration: float = np.nan

    def __post_init__(self):
        # Enforce that 'Value' column is numeric
        self.ingredients_df['Value'] = pd.to_numeric(self.ingredients_df['Value'], errors='coerce')

    def total_sum(self) -> float:
        return self.ingredients_df['Value'].sum()

    @property
    def hydration(self):
        return self._hydration
    
    @hydration.setter
    def hydration(self, value: float):
        if 0. < value <= 1.:
            self._hydration = value
        else:
            print(f'{value=} not allowed for hydration ]0,1]')

    def scale_ingredients(self, scale_factor: float) -> None:
        if scale_factor <= 0:
            return
        self.ingredients_df['Value'] *= scale_factor

    def scale_ingredient_new_quantity(self, key: Ingredients, new_quantity: float) -> None:
        assert key in self.ingredients_df.index
        old_quantity  = self.get_ingredient_quantity(key)
        scale_factor = new_quantity / old_quantity
        self.ingredients_df['Value'] *= scale_factor

    def get_ingredient_quantity(self, key: Ingredients) -> float:
        if key not in self.ingredients_df.index:
            return 0.
        value = self.ingredients_df.loc[key, 'Value']
        numeric_value = pd.to_numeric(value, errors='coerce')
        return float(numeric_value) if not pd.isna(numeric_value) else 0.
    
    def upgrade_ingredients_from_hydration(self, new_hydration: float) -> None:
        if new_hydration == self.hydration: return
        old_hydration = self.hydration
        self.hydration = new_hydration
        scale_factor = self.hydration / old_hydration
        val = pd.to_numeric(self.ingredients_df.loc[Ingredients.WATER.value, 'Value'], errors='coerce')
        if pd.isna(val):
            raise ValueError(f"Invalid value for WATER: {val}")
        self.ingredients_df.loc[Ingredients.WATER.value, 'Value'] = val * scale_factor