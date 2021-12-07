import streamlit as st
from processing import *
import pandas as pd


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
        else:
            filename = os.path.join('tmp', st.session_state['doc'].name)
            f = open(filename, 'wb+')
            f.write(st.session_state['doc'].getbuffer())
            f.close()

            with st.spinner('Downloading model...'):
                download_model()

            with st.spinner('Loading model...'):
                predict_fn = load_predict_fn()

            with st.spinner('Extracting text, exerpts, and contexts.'):
                text = pdf_to_text(filename)
                excerpts = pdf_to_excerpts(filename)
                contexts = [extract_context(excerpt, text) for excerpt in excerpts]

            outputs = []
            st.markdown('')
            st.markdown('#### ⏱️ progress')
            progress = st.progress(0)

            for e_idx, e in enumerate(zip(excerpts, contexts)):
                input = create_input(e[0], e[1])
                if input is not None:
                    output = decontextualize_excerpt(e[0], e[1], predict_fn)
                    outputs += [output]
                else:
                    outputs += [e[0]]
                progress.progress(e_idx / (len(excerpts) - 1))

            st.table(pd.DataFrame(outputs, columns=['decontextualized excerpt']))