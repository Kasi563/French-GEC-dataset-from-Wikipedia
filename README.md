# French-GEC-dataset-from-Wikipedia
This is a repository including all the code used to create and clean a Grammatical Error Correction Dataset (GEC) created from the french Wikipedia.

Wikipedia is a free encyclopedia where everyone can contribute and modify, delete, or add text to the articles. Because of this, every day there is newly created text and, most importantly, new corrections made to preexisting sentences. The idea is to find the corrections made to these sentences and create a dataset with X,y sentence pairs.

### Method
I downloaded the Wikipedia dumps from https://dumps.wikimedia.org/frwiki/ and I used xml.etree for fast parsing combined with multiprocessing to be able to go through almost all of Wikipedia (it took a while). With heavy inspiration from @daemon's pywikiclean: https://github.com/daemon/pywikiclean, I was able to convert wikimarkup into plain text, although I do not support the large number of different Wikipedia templates in French.

I spent quite a lot of time cleaning the dataset due to the difficulty of converting wikimarkup into text (especially templates). There is one major issue with this dataset (if it is used for the GEC task): a big part of the sentence pairs extracted are not in the scope of the GEC task (grammar, typos, and syntax). Many corrections made to the sentences on Wikipedia are reformulations, synthetizations, or clarifications, which, when training a model on this dataset, gives a model that reformulates and deletes parts of the sentence it was supposed to correct. To solve this problem, a classification model could be made to filter out the "bad" sentences.

### Download
The dataset is available on Kaggle: https://www.kaggle.com/datasets/isakbiderre/french-gec-dataset

### References:
[Corpora Generation for Grammatical Error Correction](https://aclanthology.org/N19-1333.pdf)
