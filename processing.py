from textwrap import wrap
import fitz
import regex as re
from nltk import sent_tokenize
import tensorflow as tf
import tensorflow_text
import requests
import os


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
                excerpt = extract_annot(annot, words)
                excerpt = excerpt.strip()
                excerpt = re.sub(r'\s+', ' ', excerpt)
                excerpts += [excerpt]

    return excerpts


def pdf_to_text(filename):
    document = fitz.open(filename)
    document = ' '.join([e.get_text() for e in document])
    document = document.replace('\n', ' ')
    document = re.sub(r'\s+', ' ', document)
    return document


def extract_context(excerpt, document, size=400):
    
    excerpt_start = re.search(re.escape(excerpt), document).start()
    excerpt_end = excerpt_start + len(excerpt)

    context_start = excerpt_start - size
    context_end = excerpt_end + size
    context = document[context_start:context_end]
    context = ' '.join(sent_tokenize(context)[1:-1])
    
    return context


def download_model():
    model_specific_path = 't5_base/1611267950' #t5_3B/1611333896 

    if not os.path.exists('model'):
        os.makedirs('my_folder')

    if not os.path.exists('model/saved_model.pb'):
        saved_model = requests.get('https://storage.googleapis.com/decontext_dataset/' + model_specific_path + '/saved_model.pb')
        open('model/saved_model.pb', 'wb').write(saved_model.content)

        if not os.path.exists('model/variables'):
            os.makedirs('model/variables')

        variables0 = requests.get('https://storage.googleapis.com/decontext_dataset/' + model_specific_path + '/variables/variables.data-00000-of-00002')
        open('model/variables/variables.data-00000-of-00002', 'wb').write(variables0.content)

        variables1 = requests.get('https://storage.googleapis.com/decontext_dataset/' + model_specific_path + '/variables/variables.data-00001-of-00002')
        open('model/variables/variables.data-00001-of-00002', 'wb').write(variables1.content)

        variables_index = requests.get('https://storage.googleapis.com/decontext_dataset/' + model_specific_path + '/variables/variables.index')
        open('model/variables/variables.index', 'wb').write(variables_index.content)


def load_predict_fn():
    imported = tf.saved_model.load('./model', ['serve'])
    return lambda x: imported.signatures['serving_default'](tf.constant(x))['outputs'].numpy()


def create_input(excerpt, context):
    context_sents = sent_tokenize(context)
    size = 1
    wrapper = None

    while size < len(context_sents) and wrapper is None:
        left = 0

        while left + size <= len(context_sents) and wrapper is None:
            if excerpt in ' '.join(context_sents[left:left + size]):
                wrapper = (left, left + size)
            left += 1

        size += 1

    if wrapper == None:
        return None

    prefix = ' '.join(context_sents[:wrapper[0]])
    target = ' '.join(context_sents[wrapper[0]:wrapper[1]])
    suffix = ' '.join(context_sents[wrapper[1]:])
    return ' [SEP] '.join(['', '', prefix, target, suffix])


def decontextualize_excerpt(excerpt, context, predict_fn):
    input = create_input(excerpt, context)
    if input is not None:
        output = predict_fn([input])[0].decode('utf-8')
        return output.split('####')[1]

