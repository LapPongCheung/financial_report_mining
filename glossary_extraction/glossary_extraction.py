import re
import nltk, string
from sklearn.feature_extraction.text import TfidfVectorizer
import os

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
    path = '.\ipo_en_collection'
    company_list = {}
    name_list = {}
    files = os.listdir(path)

    for file in files:
        
        sections = divide_into_sections(os.path.join(path, file))
        
        #get name list
        try:
            name_sec = sections[list(filter(re.compile('DIRECTORS|Directors').search, sections.keys()))[0]]
        except:
            continue
        #regex = re.compile(r'Mr\..*')
        regex = re.compile(u'\W+[\u4e00-\u9fff]+')
        names = [(n, each) for n, each in enumerate(name_sec) if re.search(regex, each)]
        
        temp_name_list = {}

        
        for name in names:
            """
            parts = name[1].strip('Mr. ').strip(')\n').split(' (')
            if len(parts) ==2:
                temp_name_list[parts[0]] = parts[1]
            else:
                temp_name_list[parts[0]] = name_sec[name[0]+1].strip('(').strip(')\n')
                """
            regex = re.compile(r'[a-zA-Z]+.*[\u4e00-\u9fff]+')
            if re.search(regex, name[1]):
                parts = re.split('[（）()\']', name[1])
                eng = re.split('\s\s+', parts[0].strip('\n'))[0]
                ch = re.search(u'[\u4e00-\u9fff]+', name[1])[0]
                if len(ch)>=2 and len(ch) <= 8:
                    temp_name_list[eng] = ch
            else:
                parts = re.split('[（）\']', name[1])
                ch = re.search(u'[\u4e00-\u9fff]+', name[1])[0]
                if name_sec[name[0]-1].strip('\n') != ('' or 'Non-executive' or 'Executive Directors'):
                    eng = name_sec[name[0]-1].strip('\n')
                else:
                    eng = name_sec[name[0]-2].strip('\n')
                eng = re.split('\s\s+', eng.strip('\n'))[0]
                if len(ch)>=2 and len(ch) <= 8:
                    temp_name_list[eng] = ch

                
        name_list.update(temp_name_list)
                
        #get company name
        heading = sections[list(sections.keys())[1]]
        for n, each in enumerate(heading):
            if re.compile(u'[\u4e00-\u9fff]+').search(each):
                if len(heading[n-1].strip('\n').strip()) >= 15 and len(heading[n-1].strip('\n').strip()) <= 35:
                    company_list[heading[n-1].strip('\n').strip()] = heading[n].strip('\n').replace(" ", "")
    
    
