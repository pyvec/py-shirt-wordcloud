
all: wordcloud.png wordcloud-yellow.svg wordcloud-blue.svg

wordcloud.png wordcloud-blue.png wordcloud-yellow.png: make_wordcloud.py pyvo.cz-content/brno.txt pyvo.cz-content/praha.txt pyvo.cz-content/ostrava.txt
	python3 make_wordcloud.py

%.bmp: %.png
	convert $< -negate $@

wordcloud-blue.svg: wordcloud-blue.bmp
	potrace --svg --color '#6CBBFB' $<

wordcloud-yellow.svg: wordcloud-yellow.bmp
	potrace --svg --color '#F7CD44' $<

pyvo.cz-content/%.txt:
	links -dump http://pyvo.cz/$* > pyvo.cz-content/$*.txt

clean:
	rm wordcloud*.png wordcloud*.bmp wordcloud*.svg || :

.PHONY: clean all
