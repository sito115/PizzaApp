from streamlit.delta_generator import DeltaGenerator
import streamlit as st
from fpdf import FPDF
from mistletoe import markdown
import io


def generate_recipe_pdf(markdown_text: str) -> io.BytesIO:  
    html = markdown(markdown_text)
    pdf = FPDF()
    pdf.set_font('Arial',size=12)
    pdf.add_page()
    pdf.write_html(html)
    return io.BytesIO(pdf.output())


def generate_print_button(col : DeltaGenerator):
    col.button('Get the recipe as PDF! :open_book:', key='is_download_pdf')
    if st.session_state.is_download_pdf:
        col.download_button(
        label='Download',
        data=generate_recipe_pdf(st.session_state.recipe_text),
        file_name='pizza_recipe.pdf',
        mime='application/pdf'
        )   