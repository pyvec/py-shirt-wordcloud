
all: wordcloud.png

wordcloud.png wordcloud-blue.png wordcloud-yellow.png: make_wordcloud.py pyvo.cz-content/brno.txt pyvo.cz-content/praha.txt pyvo.cz-content/ostrava.txt
	python3 make_wordcloud.py

pyvo.cz-content/%.txt:
	links -dump http://pyvo.cz/$* > pyvo.cz-content/$*.txt
