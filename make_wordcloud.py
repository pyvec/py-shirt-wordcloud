import re
import collections

from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import numpy as np
from PIL import Image
from scipy.misc import imread

coloring = np.array(Image.open("logo.png"))

more_stopwords = {'na', 'se', '38a', 'www', 'je', 'co', 'si', 'cz', 'po', 'že',
                  'od', 'než', 'nás', 'tak', 'na', 'za', 'pro', 'ale', 'už',
                  'či', 'cca', 'již', 'ke', 'pak', 'ze', 'až', 'při', 'kde',
                  'dá', 'ať', 'tím', 've', 'kdo'}
STOPWORDS = STOPWORDS.union(more_stopwords)

documents = []
for name in 'pyvo-brno.txt', 'pyvo-praha.txt', 'pyvo-ostrava.txt':
    with open(name, 'r') as f:
        documents.append(f.read())
words = '\n'.join(documents)
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
words = words.replace('open source', 'open-source')

words = re.split('[ \n\t.,:;!?()/@*]+', words)
counter = collections.Counter(w for w in words if
                              w not in STOPWORDS and
                              w.lower() not in STOPWORDS and
                              len(w) > 1 and
                              re.match('.*[a-z].*', w))
counter['Petr'] = counter['Viktorin']
counter['bude'] = counter['Pyvo']
del counter['Praha']
del counter['Brno']
del counter['Ostravaq']

wordcloud = WordCloud(
                      #font_path='flux.ttf',
                      font_path='/home/pviktori/.fonts/gf/BreeSerif-Regular.ttf',
                      background_color='black',
                      width=18000,
                      height=14000,
                      prefer_horizontal=0.8,
                      max_words=400,
                      mask=coloring,
                     ).generate_from_frequencies(counter.items())

image_colors = ImageColorGenerator(coloring)

wordcloud.recolor(color_func=image_colors)
wordcloud.to_file("wordcloud.png")
