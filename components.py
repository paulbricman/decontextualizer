import streamlit as st
from processing import *
import pandas as pd


def hero_section():
    hide_streamlit_style = '''
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                </style>
                '''
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    
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
            if not os.path.exists('tmp'):
                os.makedirs('tmp')
                
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
                    print('(*) ERROR', e[0], e[1])
                    st.warning('<' + e[0] + '|' + e[1] + '>')
                    outputs += [e[0]]
                progress.progress(e_idx / (len(excerpts) - 1))

            with st.expander('table'):
                st.table(pd.DataFrame(outputs, columns=['decontextualized excerpt']))

            with st.expander('text'):
                st.markdown('\n\n'.join(outputs))


def footer_section():
    footer = '''
    ---
    <style>
    button {
        border: 4px solid;
        border-color: #228b22;
        border-radius: 4px;
        background-color: #228b22;
        color: #fffffd;
        font-weight: bold;
        padding-left: 5px;
        padding-right: 5px;
    }
    </style>
    <center>
        <div>
            <a href="https://paulbricman.com/contact"><button>send feedback</button></a>
            <a href="https://github.com/paulbricman/lexiscore"><button>learn more</button></a>
            <a href="https://github.com/sponsors/paulbricman"><button>support me 🤍</button></a>
        </div>
    </center>
    '''

    st.markdown(footer, unsafe_allow_html=True)