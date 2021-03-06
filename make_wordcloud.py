import re
import collections
import os
import subprocess
import unicodedata
import random

from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import numpy as np
from PIL import Image
from scipy.misc import imread

coloring = np.array(Image.open("logo.png"))
blue_img = np.array(Image.open("logo-blue-margin.png"))
yellow_img = np.array(Image.open("logo-yellow-margin.png"))
background_img = np.array(Image.open("logo-background.png"))

more_stopwords = {'na', 'se', '38a', 'www', 'je', 'co', 'si', 'cz', 'po', 'že',
                  'od', 'než', 'nás', 'tak', 'na', 'za', 'pro', 'ale', 'už',
                  'či', 'cca', 'již', 'ke', 'pak', 'ze', 'až', 'při', 'kde',
                  'dá', 'ať', 'tím', 've', 'kdo', 'který', 'která', 'které',
                  'když', 'nebo', 'angl', 'aby', 'být', 'třeba', 'před', '36m',
                  'přes', 'nich', 'což', 'není', 'jsi', 'měla', 'jako', 'jsou',
                  'máš', 'musí', 'tam', 'ti', 'pod', 'ní', 'tomu', 'tu', 'kdy',
                  'jsem', 'atd', 'byli', 'své', 'má', 'https', 'ho', 'jpg',
                  'budu', 'jsme', 'images', 'měl', 'byla', 'jen', 'min', 'ale',
                  'ne', 'nic', 'toho', 'mě', 'html', 'nám', 'tento', 'org',
                  'takže', 'něco', 'může', 'můžete', 'jak', 'tom', 'tedy',
                  'ještě', 'pokud', 'pomocí', 'všechno', 'všechny', 'další',
                  'weight', 'color', 'bold', 'font', '350px', '0m', 'např',
                  'brno', 'praha', 'ostrava'}
STOPWORDS = STOPWORDS.union(more_stopwords)

class Term:
    def __init__(self):
        self.variants = collections.Counter()
        self.contexts = collections.Counter()
        self.contexts[random.choice(['blog', 'pyvo'])] += 0.001

    def add(self, word, context, n=1):
        self.variants[word] += n
        self.contexts[context] += n

    @classmethod
    def normalize(cls, name):
        normalized = unicodedata.normalize('NFKD', name.lower())
        return re.sub('[^a-z]', '', normalized)

    @property
    def word(self):
        return self.variants.most_common(1)[0][0]

    @property
    def occurences(self):
        return sum(self.contexts.values())

    @property
    def context(self):
        for context, n in self.contexts.most_common():
            if context != 'materialy':
                return context


term_dict = {}

def text_to_frequencies(text):
    words = text
    words = words.replace('Na Věnečku', 'Na Věnečku')
    words = words.replace('U Dřeváka', 'U Dřeváka')
    words = words.replace('pull request', 'pull request')
    words = words.replace('Pull Request', 'pull request')
    words = words.replace('Pull request', 'pull request')
    words = words.replace('Czech Republic', 'Czech Republic')
    words = words.replace('Django-cs', 'Django')
    words = words.replace('PyVo', 'Pyvo')
    words = words.replace('Barton', 'Bartoň')
    words = words.replace('Vejrazka', 'Vejražka')
    words = words.replace('Jiri', 'Jiří')
    words = words.replace('Ales', 'Aleš')
    words = words.replace('Verca', 'Verča')
    words = words.replace('open source', 'open source')
    words = words.replace('python', 'Python')
    words = words.replace('github', 'GitHub')
    words = words.replace('pycon', 'PyCon')
    words = words.replace('PyCon CZ', 'PyCon CZ')
    words = words.replace('PyCon', 'PyCon CZ')
    words = words.replace('PyCon CZ CZ', 'PyCon CZ')
    words = words.replace('twitter', 'Twitter')
    words = words.replace('facebook', 'Facebook')
    words = words.replace('Roudnice_nad_Labem', 'Roudnice nad Labem')
    words = words.replace('Pythonu', 'Python')
    words = words.replace('brnenske', 'Brněnské')
    words = words.replace('brněnské', 'Brněnské')
    words = words.replace('honzajavorek', 'Honza Javorek')
    words = words.replace('cisla', 'čísla')
    words = words.replace('pyvec', 'Pyvec')

    words = re.split('[][ \n\t`$".,:;!?()/@*-]+', words)
    counter = collections.Counter(w for w in words if
                                w not in STOPWORDS and
                                w.lower() not in STOPWORDS and
                                len(w) > 1 and
                                re.match(r'^[^#\\<>={}%_]*[a-z][^<>={}%_]*$', w))

    counter['python.cz'] = counter['Python']
    del counter['Python']

    if counter.get('Petr'):
        counter['Petr'] = min(counter.get('Honza', 0), counter.get('Petr', 0))
    if counter.get('Honza'):
        counter['Honza'] = min(counter.get('Honza', 0), counter.get('Petr', 0))
    if counter.get('Viktorin'):
        counter['Viktorin'] = min(counter.get('Javorek', 0), counter.get('Viktorin', 0))
    if counter.get('Javorek'):
        counter['Javorek'] = min(counter.get('Javorek', 0), counter.get('Viktorin', 0))
    if counter.get('Na Věnečku'):
        counter['Na Věnečku'] /= 2
    if counter.get('Ostrovského'):
        counter['Ostrovského'] /= 2
    if counter.get('print'):
        counter['print'] /= 1.5
    if counter.get('GitHub'):
        counter['GitHub'] /= 2
    counter['Pražské'] = counter['Brněnské'] = counter['Ostravské'] = (
        counter.get('Pražské', 0) + counter.get('Brněnské', 0)
        + counter.get('Ostravské', 0)) / 3
    return counter

def add_text(text, context, bias=1):
    counter = text_to_frequencies(text)
    for word, n in counter.items():
        key = Term.normalize(word)
        term = term_dict.setdefault(key, Term())
        term.add(word, context, n * bias)

def frequencies_for_context(context=None):
    return list((term.word, term.occurences) for term in term_dict.values()
                if context is None or term.context == context)

for name in 'pyvo-brno.txt', 'pyvo-praha.txt', 'pyvo-ostrava.txt':
    with open(name, 'r') as f:
        add_text(f.read(), 'pyvo')

for dirpath, dirnames, filenames in os.walk('./pyladies.cz/original/v1'):
    for filename in filenames:
        if filename.endswith('.html'):
            fullname = os.path.join(dirpath, filename)
            out = subprocess.check_output(['links', '-dump', fullname])
            add_text(out.decode('utf-8'), 'materialy')

BAD_POSTS = (
    # bez diakritiky :( 
    '2013-11-29-python-meetup-praha-listopad.md',
    '2013-12-20-python-meetup-praha-prosinec.md',
    '2014-01-18-python-meetup-praha-leden.md',
    '2014-05-23-python-meetup-praha-kveten.md',
)

for dirpath, dirnames, filenames in os.walk('./blog.python.cz/content'):
    for filename in filenames:
        if filename.endswith('.md') and filename not in BAD_POSTS:
            fullname = os.path.join(dirpath, filename)
            with open(fullname) as f:
                while f.readline().strip():
                    "skip block of declarations before first newline"
                add_text(f.read(), 'blog')


for dirpath, dirnames, filenames in os.walk('./naucse.python.cz/lessons'):
    for filename in filenames:
        if filename.endswith(('.md', '.html')):
            fullname = os.path.join(dirpath, filename)
            with open(fullname) as f:
                add_text(f.read(), 'materialy')


print(len(term_dict), 'terms')
print(term_dict['brnenske'].variants)
print(term_dict['prazske'].variants)
print(term_dict['ostravske'].variants)
for ctx in set(t.context for t in term_dict.values()):
    print(ctx, len(frequencies_for_context(ctx)))


for context in set(t.context for t in term_dict.values()) | {'materialy'}:
    total = sum(t.contexts.get(context, 0) for t in term_dict.values())
    if context == 'materialy':
        total /= 2
    print(context, total)
    for term in term_dict.values():
        if context in term.contexts:
            term.contexts[context] /= total


default_random = random.Random()

def color_func(word, font_size, position, orientation, font_path, random_state):
    if random_state is None:
        random_state = default_random

    mini = 0
    maxi = 255
    saturation = 80
    lightness = 50
    term = term_dict[Term.normalize(word)]
    context = term.context
    if context == 'blog':
        hue = 207
        saturation = 80
        lightness = 65
    elif context == 'pyvo':
        hue = 46
        saturation = 70
        lightness = 50
    elif context == 'materialy-xx':
        mini = 0
        maxi = 5
        return "rgb(255, 255, 255)"
    return "hsl({}, {}%, {}%)".format(int(round(hue)),
                                      int(round(saturation)),
                                      int(round(lightness)))


def make_wordcloud(context, img):
    print('Making wordcloud:', context)
    return WordCloud(
        #font_path='flux.ttf',
        font_path='./3rd-party/breeserif/BreeSerif-Regular.ttf',
        background_color='black',
        width=1372,
        height=1372,
        prefer_horizontal=0.8,
        max_words=500,
        relative_scaling=0.5,
        scale=7,
        color_func=color_func,
        mask=img,
       ).generate_from_frequencies(frequencies_for_context(context))

blue_array = make_wordcloud('blog', blue_img).to_array()
yellow_array = make_wordcloud('pyvo', yellow_img).to_array()

array = blue_array + yellow_array

print('Saving images')

Image.fromarray(array).save("wordcloud.png")

Image.fromarray(blue_array).save("wordcloud-blue.png")
Image.fromarray(yellow_array).save("wordcloud-yellow.png")
