import streamlit as st
import components
import nltk

nltk.download('punkt')

st.set_page_config(
    page_title='decontextualizer',
    #layout='wide',
    menu_items={
        'Get help': 'https://github.com/paulbricman/decontextualizer/issues',
        'Report a Bug': 'https://github.com/paulbricman/decontextualizer/issues/new',
        'About': 'https://paulbricman.com/thoughtware'
    })

components.hero_section()
components.add_section()
components.footer_section()