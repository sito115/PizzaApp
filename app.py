import streamlit as st
import pandas as pd
from typing import Union
from dough_class import Ingredients, Dough
from streamlit.delta_generator import DeltaGenerator
from helpers import generate_print_button


INIT_FLOUR: float = 1000.
INIT_HYDRATION: float = 0.7
INIT_POULISH_MAIN_RATIO: float = 0.3
INIT_WEIGHT_PER_PIZZA: float = 250.
PAGE_TITLE = 'Pizza Dough Calculator 1.2'


poulish_ingredients: dict[str, Union[float, int]] = {
    Ingredients.FLOUR: 300,
    Ingredients.WATER: 300,
    Ingredients.YEAST: 6,
    Ingredients.HONEY: 5,
}

main_dough_ingredients: dict[str, Union[float, int]] = {
    Ingredients.FLOUR: 700,
    Ingredients.WATER: 400,
    Ingredients.OLIVE_OIL: 10,
    Ingredients.SALT: 25,
}

poulish_dough = Dough(ingredients_df = pd.DataFrame([300, 300, 6, 5],
                                                    columns=['Value'], 
                                                    index = [Ingredients.FLOUR, Ingredients.WATER,
                                                            Ingredients.YEAST, Ingredients.HONEY]))

main_dough = Dough(ingredients_df = pd.DataFrame([700, 400, 10, 25],
                                                columns=['Value'],
                                                index = [Ingredients.FLOUR, Ingredients.WATER,
                                                        Ingredients.OLIVE_OIL, Ingredients.SALT]))
main_dough.hydration = INIT_HYDRATION

INIT_N_PIZZAS = (poulish_dough.total_sum() + main_dough.total_sum()) / INIT_WEIGHT_PER_PIZZA



def update_ingredients_table():
    st.session_state['main_dough'].upgrade_ingredients_from_hydration(st.session_state.hydration)

    st.session_state['poulish'].scale_ingredient_new_quantity(st.session_state.key_ingredient,
                                                               st.session_state.poulish_main_dough_ratio*st.session_state.key_ingredient_input)
    st.session_state['main_dough'].scale_ingredient_new_quantity(st.session_state.key_ingredient,
                                                                  (1 - st.session_state.poulish_main_dough_ratio)* st.session_state.key_ingredient_input)    
    total_sum = st.session_state['poulish'].total_sum() + st.session_state['main_dough'].total_sum()
    st.session_state['total_pizzas'] = total_sum / st.session_state.weight_per_pizza


def update_key_ing_input():
    st.session_state.key_ingredient_input = st.session_state.key_ingredient_slider
    update_ingredients_table()
    
    
def update_key_ing_slider():
    st.session_state.key_ingredient_slider = st.session_state.key_ingredient_input
    update_ingredients_table()


def view_key_ingredient_quantities():
    poulish_quantity = st.session_state['poulish'].get_ingredient_quantity(st.session_state.key_ingredient) 
    main_dough_quantity = st.session_state['main_dough'].get_ingredient_quantity(st.session_state.key_ingredient) 
    st.session_state.key_ingredient_input = poulish_quantity + main_dough_quantity
    st.session_state.key_ingredient_slider = poulish_quantity + main_dough_quantity


def update_total_pizza_amount():
    current_amount = st.session_state['total_sum']
    new_amount = st.session_state['total_pizzas'] * st.session_state['weight_per_pizza']
    factor = new_amount / current_amount
    st.session_state['poulish'].scale_ingredients(factor)
    st.session_state['main_dough'].scale_ingredients(factor)
    view_key_ingredient_quantities()


def initilise_session():
    if 'poulish' not in st.session_state:
        st.session_state['poulish'] = poulish_dough

    if 'main_dough' not in st.session_state:
        st.session_state['main_dough'] = main_dough
        st.session_state['main_dough'].hydration = INIT_HYDRATION
    
    if 'total_pizzas' not in st.session_state:
        st.session_state['total_pizzas'] = INIT_N_PIZZAS
    
    if 'weight_per_pizza' not in st.session_state:
        st.session_state['weight_per_pizza'] = INIT_WEIGHT_PER_PIZZA 

    if 'key_ingredient_input' not in st.session_state:
        st.session_state['key_ingredient_input'] = INIT_FLOUR 

    if 'poulish_main_dough_ratio' not in st.session_state:    
        st.session_state['poulish_main_dough_ratio'] = INIT_POULISH_MAIN_RATIO

    if 'hydration' not in st.session_state:
        st.session_state['hydration'] = INIT_HYDRATION

    st.session_state.key_ingredient_slider = st.session_state.key_ingredient_input

    st.session_state['total_sum'] = st.session_state['poulish'].total_sum() + st.session_state['main_dough'].total_sum()

    recipe_text = f'''
# Pizza Recipe

Generated with the [Pizza Dough Calculator App](https://pizzadoughcalculator.streamlit.app/).
Yields {st.session_state['total_pizzas']:.0f} pizzas à {st.session_state['weight_per_pizza']:.1f} g.

### Poulish
1. Dissolve {st.session_state['poulish'].get_ingredient_quantity(Ingredients.YEAST):.1f} grams of yeast in {st.session_state['poulish'].get_ingredient_quantity(Ingredients.WATER):.1f} mL of water.
2. Add {st.session_state['poulish'].get_ingredient_quantity(Ingredients.HONEY):.1f} g of honey and dissolve.
3. Add {st.session_state['poulish'].get_ingredient_quantity(Ingredients.FLOUR):.1f} g of flour and mix.
4. Cover the poulish in an airtight  container and let it rest for 30 min at room temperature.
5. Then, put it in the frigde for 16 - 24h.

### Main Dough
1. Take the poulish out of the fridge ca. 30 min before starting the main dough.
2. Add {st.session_state['main_dough'].get_ingredient_quantity(Ingredients.WATER):.1f} mL and dissolve the poulish.
3. Add {st.session_state['main_dough'].get_ingredient_quantity(Ingredients.FLOUR):.1f} g of flour and knead for 10 min.
4. Add {st.session_state['main_dough'].get_ingredient_quantity(Ingredients.SALT):.1f} g of salt and knead for 5 min.
5. When the dough starts to become stick, add {st.session_state['main_dough'].get_ingredient_quantity(Ingredients.OLIVE_OIL):.1f} g of olive oil.
6. Then, place the dough in the frigde for 16 - 24h.
7. Take the dough out of the fridge ca. 30 min before forming the doigh balls. 
8. Divide the dough into {st.session_state['total_pizzas']:.0f} balls à {st.session_state['weight_per_pizza']:.1f} g.
9. Let them rest for min. 1.5 h.
'''
        
    st.session_state['recipe_text'] = recipe_text


def generate_reset_button(col : DeltaGenerator):
    col.button('Reset', key='is_reset')
    if st.session_state.is_reset:
        st.session_state.key_ingredient_input = INIT_FLOUR
        st.session_state.key_ingredient_slider = INIT_FLOUR
        st.session_state.hydration = INIT_HYDRATION
        st.session_state.poulish_main_dough_ratio = INIT_POULISH_MAIN_RATIO
        st.session_state.key_ingredient =Ingredients.FLOUR

        st.session_state['poulish'] = poulish_dough
        st.session_state['main_dough'] = main_dough

        update_ingredients_table()
        st.session_state.total_pizzas = INIT_N_PIZZAS
        st.session_state.weight_per_pizza = INIT_WEIGHT_PER_PIZZA




def generate_base_settings(expander: DeltaGenerator):
    with expander:

        col1, col2 = st.columns(2)

        with col1:

            st.selectbox(
                'Select an ingredient to set the proportions of the recipe.',
                [Ingredients.FLOUR, Ingredients.WATER],
                key='key_ingredient',
                on_change=view_key_ingredient_quantities
            )

            st.write(f'How much {st.session_state.key_ingredient.lower()} are you going to use?')

            st.number_input(f'{st.session_state.key_ingredient}',
                            key = 'key_ingredient_input',
                            min_value = 0.,
                            max_value = 10_000.,
                            # value=INIT_FLOUR,
                            step = 100.,
                            on_change = update_key_ing_slider)

            st.slider(f'{st.session_state.key_ingredient}',
                        key = 'key_ingredient_slider',
                        min_value = 0.,
                        max_value = 10_000.,
                        # value=INIT_FLOUR,
                        step=50.,
                        on_change = update_key_ing_input)

        with col2:
            st.number_input('Total amount of pizzas [-]', 
                            min_value=1. ,
                            key= 'total_pizzas',
                            step=1.,
                            on_change=update_total_pizza_amount)
            
            st.number_input('Weight per pizza [g]',
                            min_value=1. ,
                            key= 'weight_per_pizza',
                            step=10.,
                            on_change= update_total_pizza_amount)
            
            st.write(f'Total weight is ca. {st.session_state.total_sum:,.2f} g.')
            st.write(f'Total weight results in ca. {st.session_state.total_sum/st.session_state.weight_per_pizza:.0f} Pizzas a {st.session_state.weight_per_pizza} g.')    

def generate_advanced_settings(expander: DeltaGenerator):
    with expander:
        
        st.slider('Poulish - Main Dough Ratio [%]',
                    key = 'poulish_main_dough_ratio',
                    min_value = 0.,
                    max_value = 1.,
                    on_change=update_ingredients_table,
                    help = 'How much poulish dough in relation to the main dough.')

        st.slider('Hydration [%]',
                    key = 'hydration',
                    min_value = 0.,
                    max_value = 1.,
                    on_change=update_ingredients_table,
                    help = 'E.g. a hydration of 70% means that in the final dough the water to flour ration is 70%.')


def main():

    initilise_session()

    st.set_page_config(page_title=PAGE_TITLE,
                       page_icon = ':pizza:')
    st.write("[![Star](https://img.shields.io/github/stars/sito115/PizzaApp.svg?logo=github&style=social)](https://github.com/sito115/PizzaApp)")


    st.image('Pizza.jpg', use_container_width=True)
    st.title(PAGE_TITLE)

    left_column, right_column = st.columns(2)
    generate_reset_button(left_column)
    generate_print_button(right_column)

    expand_recipe = st.expander('Recipe')
    with expand_recipe:
        st.write(st.session_state.recipe_text)

    expand_base = st.expander('Base Settings', expanded=True)
    generate_base_settings(expand_base)

    expand_advanced = st.expander('Advanced Settings')
    generate_advanced_settings(expand_advanced)
    

    expand_ingredients = st.expander('Ingredients', expanded=True)
    with expand_ingredients:

        st.dataframe(st.session_state['poulish'].ingredients_df,
                    use_container_width = True,
                    column_config=None,
                    key = 'table_poulish')           

        st.dataframe(st.session_state['main_dough'].ingredients_df,
                    use_container_width = True,
                    column_config=None,
                    key = 'table_dough')                              


        
    # st.write(st.session_state)


if __name__ == '__main__':

    main()
