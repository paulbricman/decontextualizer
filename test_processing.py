from processing import pdf_to_text, pdf_to_excerpts, extract_context


def test_context_extraction():
    filename = 'data/annotated1.pdf'
    document = pdf_to_text(filename)
    excerpts = pdf_to_excerpts(filename)
    
    contexts = [extract_context(excerpt, document) for excerpt in excerpts]
    print(*[e for e in zip(excerpts, contexts)], sep='\n\n')

test_context_extraction()