import re
import nltk, string
from sklearn.feature_extraction.text import TfidfVectorizer

def page_break(file):
	f = open(file, 'r', encoding = 'utf-8')
	lines = f.readlines()

	breaks = []

	for num, line in enumerate(lines):
		if '\f' in line:
			breaks.append(num)

	return breaks

def divide_into_sections(file):
	f = open(file, 'r', encoding = 'utf-8')
	lines = f.readlines()

	breaks = []

	for num, line in enumerate(lines):
		if '\f' in line:
			breaks.append(num)
	#remove special line "JOBNAME"
	new_breaks = []
	for i in range(len(breaks)):
		if r'JOBNAME' in lines[breaks[i]]:
			new_breaks.append(breaks[i] + 2)
		else:
			new_breaks.append(breaks[i])
	breaks = new_breaks

	sections = {}
	title = ''
	previous_title = ''
	current_section = []
	for i in range(len(breaks)):
		title = lines[breaks[i]]
		if title != previous_title and i != 1:
			sections[previous_title] = current_section
			current_section = []
		try:
			content = lines[breaks[i]:breaks[i+1]]
		except:
			content = lines[breaks[i]:-1]
			current_section.extend(content)
			sections[title] = current_section
			break
		current_section.extend(content)
		previous_title = title

	return sections

def stem_tokens(tokens):
    return [stemmer.stem(item) for item in tokens]

'''remove punctuation, lowercase, stem'''
def normalize(text):
    return stem_tokens(nltk.word_tokenize(text.lower().translate(remove_punctuation_map)))


def cosine_sim(text1, text2):
    tfidf = vectorizer.fit_transform([text1, text2])
    return ((tfidf * tfidf.T).A)[0,1]



if __name__ == "__main__":
    link_1 = r'./testing_data/06080'
    sections_1 = divide_into_sections(link_1)
    
    link_2 = r'./testing_data/08413'
    sections_2 = divide_into_sections(link_2)
    
    stemmer = nltk.stem.porter.PorterStemmer()
    remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)
    vectorizer = TfidfVectorizer(tokenizer=normalize, stop_words='english')
    
    common = set(sections_1.keys()) & set(sections_2.keys())
    
    for each in common:
        try:
            text1 = ''.join(sections_1[each])
            text2 = ''.join(sections_2[each])
        
            print ('TF-IDF score of ' + each + ': ' + str(cosine_sim(text1, text2)))
        except:
            pass
        
    print ('baseline "a little bird', 'a little bird chirps": ' + str(cosine_sim('a little bird', 'a little bird chirps')))
    print ('baseline "a little bird', 'a big dog barks": ' + str(cosine_sim('a little bird', 'a big dog barks')))
    
    
    
    
