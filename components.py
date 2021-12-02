import streamlit as st


def hero_section():
    st.title('📤 decontextualizer')
    st.markdown('A pipeline for making highlighted text stand-alone.')
    st.markdown('---')

def add_section():
    st.markdown('#### 📄 add document')
    st.session_state['doc'] = st.file_uploader('Please select the file you want to process.', type='pdf')
    
    if st.button('start processing'):
        if st.session_state['doc'] is None:
            st.warning('Please specify a file.')