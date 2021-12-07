from processing import *


def test_context_extraction():
    download_model()
    predict_fn = load_predict_fn()

    print('[*] Model loaded')

    filename = 'data/annotated1.pdf'
    document = pdf_to_text(filename)
    excerpts = pdf_to_excerpts(filename)
    contexts = [extract_context(excerpt, document) for excerpt in excerpts]
    
    print('[*] Excerpts and contexts loaded')

    for e_idx, e in enumerate(zip(excerpts, contexts)):
        input = create_input(e[0], e[1])
        output = decontextualize_excerpt(e[0], e[1], predict_fn)

test_context_extraction()