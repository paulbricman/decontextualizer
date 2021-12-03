import fitz


def check_contain(r_word, points):
    r = fitz.Quad(points).rect
    r.intersect(r_word)

    if r.get_area() >= r_word.get_area() * 0.1:
        contain = True
    else:
        contain = False
    return contain


def extract_annot(annot, words_on_page):
    quad_points = annot.vertices
    quad_count = int(len(quad_points) / 4)
    sentences = ['' for i in range(quad_count)]
    for i in range(quad_count):
        points = quad_points[i * 4: i * 4 + 4]
        words = [
            w for w in words_on_page if
            check_contain(fitz.Rect(w[:4]), points)
        ]
        sentences[i] = ' '.join(w[4] for w in words)
    sentence = ' '.join(sentences)

    return sentence


def pdf_to_excerpts(filename):
    doc = fitz.open(filename)
    excerpts = []

    for page_idx, page in enumerate(doc):
        words = page.get_text('words')
        annots = page.annots()
        
        for annot in annots:
            if annot is not None:
                excerpts += [extract_annot(annot, words)]

    return excerpts


def pdf_to_text(filename):
    doc = fitz.open(filename)
    text = ' '.join([e.get_text() for e in doc])
    return text
