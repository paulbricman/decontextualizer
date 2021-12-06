import fitz
import regex as re
from nltk import sent_tokenize
import tensorflow as tf
import tensorflow_text
import requests


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


def extract_context(excerpt, document, size=400):
    document = document.replace('\n', ' ')
    excerpt = excerpt.strip()

    excerpt = re.sub(r'\s+', ' ', excerpt)
    document = re.sub(r'\s+', ' ', document)
    
    excerpt_start = re.search(re.escape(excerpt), document).start()
    excerpt_end = excerpt_start + len(excerpt)

    context_start = excerpt_start - size
    context_end = excerpt_end + size
    context = document[context_start:context_end]
    context = ' '.join(sent_tokenize(context)[1:-1])
    
    return context


def download_model():
    saved_model = requests.get('https://storage.googleapis.com/decontext_dataset/t5_base/1611267950/saved_model.pb')
    open('model/saved_model.pb', 'wb').write(saved_model.content)

    variables0 = requests.get('https://storage.googleapis.com/decontext_dataset/t5_base/1611267950/variables/variables.data-00000-of-00002')
    open('model/variables/variables.data-00000-of-00002', 'wb').write(variables0.content)

    variables1 = requests.get('https://storage.googleapis.com/decontext_dataset/t5_base/1611267950/variables/variables.data-00001-of-00002')
    open('model/variables/variables.data-00001-of-00002', 'wb').write(variables1.content)

    variables_index = requests.get('https://storage.googleapis.com/decontext_dataset/t5_base/1611267950/variables/variables.index')
    open('model/variables/variables.index', 'wb').write(variables_index.content)


def load_predict_fn():
    imported = tf.saved_model.load('./model', ['serve'])
    return lambda x: imported.signatures['serving_default'](tf.constant(x))['outputs'].numpy()


def decontextualize(input):
  return predict_fn([input])[0].decode('utf-8')


# download_model()
predict_fn = load_predict_fn()

paragraph = [
  "Gagarin was a keen sportsman and played ice hockey as a goalkeeper.",
  "He was also a basketball fan and coached the Saratov Industrial Technical School team, as well as being a referee.",
  "In 1957, while a cadet in flight school, Gagarin met Valentina Goryacheva at the May Day celebrations at the Red Square in Moscow.",
  "She was a medical technician who had graduated from Orenburg Medical School.",
  "They were married on 7 November of the same year, the same day Gagarin graduated from his flight school, and they had two daughters.",
  "Yelena Yurievna Gagarina, born 1959, is an art historian who has worked as the director-general of the Moscow Kremlin Museums since 2001; and Galina Yurievna Gagarina, born 1961, is a professor of economics and the department chair at Plekhanov Russian University of Economics in Moscow."
]

page_title = 'Yuri Gagarin'
section_title = 'Personal Life'  # can be empty
target_sentence_idx = 4  # zero-based index


if target_sentence_idx >= len(paragraph) or target_sentence_idx < 0:
  raise ValueError(
      f'Target sentence index must be in range [0, {len(paragraph) - 1}].')


def create_input(paragraph,
                 target_sentence_idx,
                 page_title='',
                 section_title=''):
  """Creates a single Decontextualization example input for T5.

  Args:
    paragraph: List of strings. Each string is a single sentence.
    target_sentence_idx: Integer index into `paragraph` indicating which
      sentence should be decontextualized.
    page_title: Optional title string. Usually Wikipedia page title.
    section_title: Optional title of section within page.
  """
  prefix = ' '.join(paragraph[:target_sentence_idx])
  target = paragraph[target_sentence_idx]
  suffix = ' '.join(paragraph[target_sentence_idx + 1:])
  return ' [SEP] '.join((page_title, section_title, prefix, target, suffix))

d = decontextualize(
        create_input(paragraph, target_sentence_idx, page_title,
                     section_title))
print(f'Original sentence:         {paragraph[target_sentence_idx]}\n'
      f'Decontextualized sentence: {d}')