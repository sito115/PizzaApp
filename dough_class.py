from enum import Enum
from pydantic import BaseModel, computed_field, PrivateAttr, field_validator
from typing import Union
import numpy as np

class Ingredients(Enum):
    FLOUR  = 'Flour [g]'
    WATER  = 'Water [L]'
    YEAST  = 'Yeast [g]'
    SALT   = 'Salt [g]'
    HONEY  = 'Honey [g]'
    OLIVE_OIL = 'Olive Oil [g]'

    def __str__(self):
        return self.value

class Dough(BaseModel):
    ingredients: dict[str, Union[int, float]]
    _hydration: float = np.nan
    
    @field_validator('ingredients')
    @classmethod
    def dough_contains_liquid(cls, val : dict[str, Union[int, float]]) -> dict[str, Union[int, float]]:
        keys_2_check = {Ingredients.WATER.value, Ingredients.FLOUR.value}
        if not keys_2_check.issubset(val.keys()):
            raise ValueError(f'Dough must contain {keys_2_check}')
        return val
        
    @property
    def hydration(self):
        return self._hydration
    
    @hydration.setter
    def hydration(self, value: float):
        if 0. < value <= 1.:
            self._hydration = value
        else:
            print(f'{value=} not allowed for hydration ]0,1]')

    def get_ingredient_quantity(self, key: str) -> float:
        if key in self.ingredients.keys():
            return self.ingredients[key]
        else:
            return 0.

    def upgrade_ingredients_proportion(self, key: str, value : Union[int, float]) -> None:
        if value == 0:
            return
        scale = value / self.ingredients[key]
        for key_ in self.ingredients.keys():
            self.ingredients[key_] *= scale
            
    def upgrade_liquid_from_hydration(self, new_hydration: float) -> None:
        if np.isnan(self._hydration): return
        if new_hydration == self.hydration: return
        old_hydration = self.hydration
        self.hydration = new_hydration
        self.ingredients[Ingredients.WATER.value] = self.hydration / old_hydration * self.ingredients[Ingredients.WATER.value] 

    def total_sum(self) -> float:
        return sum(self.ingredients.values())
    
    def scale_all_ingredients(self, factor: float) -> None:
        if factor <= 0:
            return
        for key in self.ingredients.keys():
            self.ingredients[key] *= factor