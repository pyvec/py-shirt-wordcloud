import re
import collections
import os
import subprocess

from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import numpy as np
from PIL import Image
from scipy.misc import imread

coloring = np.array(Image.open("logo.png"))

more_stopwords = {'na', 'se', '38a', 'www', 'je', 'co', 'si', 'cz', 'po', 'že',
                  'od', 'než', 'nás', 'tak', 'na', 'za', 'pro', 'ale', 'už',
                  'či', 'cca', 'již', 'ke', 'pak', 'ze', 'až', 'při', 'kde',
                  'dá', 'ať', 'tím', 've', 'kdo', 'který', 'která', 'které',
                  'když', 'nebo', 'angl', 'aby', 'být', 'třeba', 'před',
                  'přes', 'nich', 'což', 'není', 'jsi', 'měla', 'jako', 'jsou',
                  'máš', 'musí', 'tam', 'ti', 'pod', 'ní', 'tomu', 'tu', 'kdy',
                  'jsem', 'atd', 'byli', 'své', 'má', 'https', 'ho', 'jpg',
                  'budu', 'jsme', 'images', 'měl', 'byla', 'jen', 'min'}
STOPWORDS = STOPWORDS.union(more_stopwords)

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
    words = words.replace('open source', 'open source')
    words = words.replace('python', 'Python')
    words = words.replace('Roudnice_nad_Labem', 'Roudnice nad Labem')

    words = re.split('[][ \n\t.,:;!?()/@*-]+', words)
    counter = collections.Counter(w for w in words if
                                w not in STOPWORDS and
                                w.lower() not in STOPWORDS and
                                len(w) > 1 and
                                re.match('^[^<>={}%_]*[a-z][^<>={}%_]*$', w))

    counter['Praha'] = counter['Brno'] = counter['Ostrava'] = 0
    return counter

counter = collections.Counter()

for name in 'pyvo-brno.txt', 'pyvo-praha.txt', 'pyvo-ostrava.txt':
    with open(name, 'r') as f:
        counter += text_to_frequencies(f.read())

for dirpath, dirnames, filenames in os.walk('./pyladies.cz/original/v1'):
    for filename in filenames:
        if filename.endswith('.html'):
            fullname = os.path.join(dirpath, filename)
            out = subprocess.check_output(['links', '-dump', fullname])
            counter += text_to_frequencies(out.decode('utf-8'))

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
                counter += text_to_frequencies(f.read())


print(len(counter), 'words')

wordcloud = WordCloud(
                      #font_path='flux.ttf',
                      font_path='/home/pviktori/.fonts/gf/BreeSerif-Regular.ttf',
                      background_color='black',
                      width=1372,
                      height=1372,
                      prefer_horizontal=0.8,
                      max_words=500,
                      relative_scaling=0.5,
                      scale=7,
                      mask=coloring,
                     ).generate_from_frequencies(counter.items())

image_colors = ImageColorGenerator(coloring)

wordcloud.recolor(color_func=image_colors)
wordcloud.to_file("wordcloud.png")
