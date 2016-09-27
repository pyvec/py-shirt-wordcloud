
all: wordcloud.png wordcloud.svg wordcloud-small.png

wordcloud.png wordcloud-blue.png wordcloud-yellow.png: make_wordcloud.py pyvo.cz-content/brno.txt pyvo.cz-content/praha.txt pyvo.cz-content/ostrava.txt
	python3 make_wordcloud.py

%.bmp: %.png
	convert $< -negate $@

wordcloud-blue.svg: wordcloud-blue.bmp
	potrace --svg --group --color '#6CBBFB' $<

wordcloud-yellow.svg: wordcloud-yellow.bmp
	potrace --svg --group --color '#F7CD44' $<

wordcloud.svg: wordcloud-blue.svg wordcloud-yellow.svg
	sed '$$ d' wordcloud-blue.svg > wordcloud.svg
	tail -n +$(shell grep '<g ' wordcloud-yellow.svg -n | cut -f1 -d: | head -n 1) wordcloud-yellow.svg >> wordcloud.svg

pyvo.cz-content/%.txt:
	links -dump http://pyvo.cz/$* > pyvo.cz-content/$*.txt

clean:
	rm wordcloud*.png wordcloud*.bmp wordcloud*.svg || :

wordcloud-small.png: wordcloud.png
	convert $< -thumbnail 1000x1000 $@

.PHONY: clean all
