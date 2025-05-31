import streamlit as st
import pandas as pd
from streamlit.delta_generator import DeltaGenerator
from pathlib import Path
import sys
sys.path.insert(0 , str(Path(__file__).parents[1]))
from helpers import generate_print_button
from dough_class import Ingredients, Dough


INIT_FLOUR: float = 250 + 460.
INIT_HYDRATION: float = 0.68
INIT_POULISH_MAIN_RATIO: float = 0.3
INIT_WEIGHT_PER_PIZZA: float = 250.
PAGE_TITLE = 'Pizza Dough Calculator 1.2'

mother_yeast = Dough(ingredients_df = pd.DataFrame([250, 170, 250],
                                                    columns=['Value'], 
                                                    index = [Ingredients.FLOUR, Ingredients.WATER,
                                                            Ingredients.MOTHER_YEAST]))

main_dough = Dough(ingredients_df = pd.DataFrame([460, 300, 10, 10],
                                                columns=['Value'],
                                                index = [Ingredients.FLOUR, Ingredients.WATER,
                                                        Ingredients.OLIVE_OIL, Ingredients.SALT]))



main_dough.hydration = INIT_HYDRATION

INIT_N_PIZZAS = (mother_yeast.total_sum() - mother_yeast.get_ingredient_quantity(Ingredients.MOTHER_YEAST) + main_dough.total_sum()) / INIT_WEIGHT_PER_PIZZA



def update_ingredients_table():
    st.session_state['main_dough_s'].upgrade_ingredients_from_hydration(st.session_state.hydration)

    amount_main = st.session_state['mother_dough'].get_ingredient_quantity(st.session_state.key_ingredient)
    amount_sour = st.session_state['main_dough_s'].get_ingredient_quantity(st.session_state.key_ingredient)
    ratio = amount_sour / amount_main

    st.session_state['mother_dough'].scale_ingredient_new_quantity(st.session_state.key_ingredient,
                                                                  ratio*st.session_state.key_ingredient_input)
    st.session_state['main_dough_s'].scale_ingredient_new_quantity(st.session_state.key_ingredient,
                                                                  (1 - ratio)* st.session_state.key_ingredient_input)    
    total_sum = st.session_state['mother_dough'].total_sum() - st.session_state['mother_dough'].get_ingredient_quantity(Ingredients.MOTHER_YEAST) + st.session_state['main_dough_s'].total_sum()
    st.session_state['total_pizzas'] = total_sum / st.session_state.weight_per_pizza


def update_key_ing_input():
    st.session_state.key_ingredient_input = st.session_state.key_ingredient_slider
    update_ingredients_table()
    
    
def update_key_ing_slider():
    st.session_state.key_ingredient_slider = st.session_state.key_ingredient_input
    update_ingredients_table()


def view_key_ingredient_quantities():
    poulish_quantity = st.session_state['mother_dough'].get_ingredient_quantity(st.session_state.key_ingredient) 
    main_dough_quantity = st.session_state['main_dough_s'].get_ingredient_quantity(st.session_state.key_ingredient) 
    st.session_state.key_ingredient_input = poulish_quantity + main_dough_quantity
    st.session_state.key_ingredient_slider = poulish_quantity + main_dough_quantity


def update_total_pizza_amount():
    current_amount = st.session_state['total_sum'] - st.session_state['mother_dough'].get_ingredient_quantity(Ingredients.MOTHER_YEAST)
    new_amount = st.session_state['total_pizzas'] * st.session_state['weight_per_pizza']
    factor = new_amount / current_amount
    st.session_state['mother_dough'].scale_ingredients(factor)
    st.session_state['main_dough_s'].scale_ingredients(factor)
    view_key_ingredient_quantities()


def initilise_session():
    if 'mother_dough' not in st.session_state:
        st.session_state['mother_dough'] = mother_yeast

    if 'main_dough_s' not in st.session_state:
        st.session_state['main_dough_s'] = main_dough
        st.session_state['main_dough_s'].hydration = INIT_HYDRATION
    
    if 'total_pizzas' not in st.session_state:
        st.session_state['total_pizzas'] = INIT_N_PIZZAS
    
    if 'weight_per_pizza' not in st.session_state:
        st.session_state['weight_per_pizza'] = INIT_WEIGHT_PER_PIZZA 

    if 'key_ingredient_input' not in st.session_state:
        st.session_state['key_ingredient_input'] = INIT_FLOUR 

    if 'hydration' not in st.session_state:
        st.session_state['hydration'] = INIT_HYDRATION

    st.session_state.key_ingredient_slider = st.session_state.key_ingredient_input

    st.session_state['total_sum'] = st.session_state['mother_dough'].total_sum() - st.session_state['mother_dough'].get_ingredient_quantity(Ingredients.MOTHER_YEAST) + st.session_state['main_dough_s'].total_sum()

    recipe_text = f'''
# Pizza Recipe

Generated with the [Pizza Dough Calculator App](https://pizzadoughcalculator.streamlit.app/).

'''
        
    st.session_state['recipe_text_s'] = recipe_text


def generate_reset_button(col : DeltaGenerator):
    col.button('Reset', key='is_reset', on_click=reset)

def reset():
    st.session_state.key_ingredient_input = INIT_FLOUR
    st.session_state.key_ingredient_slider = INIT_FLOUR
    st.session_state.hydration = INIT_HYDRATION
    st.session_state.key_ingredient =Ingredients.FLOUR

    st.session_state['mother_dough'] = mother_yeast
    st.session_state['main_dough_s'] = main_dough

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
            st.write(f'Total weight results in ca. {st.session_state.total_sum /st.session_state.weight_per_pizza:.0f} Pizzas a {st.session_state.weight_per_pizza} g.')    

def generate_advanced_settings(expander: DeltaGenerator):
    with expander:
        
        st.slider('Hydration [%]',
                    key = 'hydration',
                    min_value = 0.,
                    max_value = 1.,
                    on_change=update_ingredients_table,
                    help = 'E.g. a hydration of 70% means that in the final dough the water to flour ration is 70%.')
        

def main():
    # st.set_page_config(page_title="Mapping Demo", page_icon="🌍")

    initilise_session()

    st.set_page_config(page_title=PAGE_TITLE,
                       page_icon = ':pizza:')
    st.write("[![Star](https://img.shields.io/github/stars/sito115/PizzaApp.svg?logo=github&style=social)](https://github.com/sito115/PizzaApp)")


    st.image('data/Pizza.jpg', use_container_width=True)
    st.title(PAGE_TITLE)

    left_column, right_column = st.columns(2)
    generate_reset_button(left_column)
    generate_print_button(right_column, st.session_state.recipe_text_s)

    expand_recipe = st.expander('Recipe')
    with expand_recipe:
        st.write(st.session_state.recipe_text_s)

    expand_base = st.expander('Base Settings', expanded=True)
    generate_base_settings(expand_base)

    expand_advanced = st.expander('Advanced Settings')
    generate_advanced_settings(expand_advanced)
    

    expand_ingredients = st.expander('Ingredients', expanded=True)
    with expand_ingredients:

        st.dataframe(st.session_state['mother_dough'].ingredients_df,
                    use_container_width = True,
                    column_config=None,
                    key = 'table_poulish')           

        st.dataframe(st.session_state['main_dough_s'].ingredients_df,
                    use_container_width = True,
                    column_config=None,
                    key = 'table_dough')                              


        
    # st.write(st.session_state)


if __name__ == '__main__':
    main()
