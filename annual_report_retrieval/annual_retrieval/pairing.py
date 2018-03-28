# -*- coding: utf-8 -*-

import logging
import os
import re
import string
import jieba
import sys
#import nltk
import os
#from nltk.tokenize import sent_tokenize
from itertools import permutations

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

# special tokens
sentence_stoppunc = ['.', '?', '!', '。', '！', '？', ':', ';', '：', '；']
heading_stoppunc = ['.', '?', '!', '。', '！', '？', ':', ';', '：', '；']
_TBR = '_TBR'
_PREFIXES = '_PREFIXES'
_ABBRE = '_ABBRE'
_ITEM = _TBR
# _ITEM = '_ITEM'
_NUM = '_NUM'
_HKD = '_HKD'
# _abbre = ['Ph.D.', 'a.m.', 'p.m.', 'i.e.', 'e.g.', 'Dr.', 'Mr.', 'Mrs.', 'Ms.', 'No.']

from pprint import pprint

# remove page break
def rm_x0c(text):
    return re.sub(r'\x0c', '', text) #\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff

# remove white space at the begining/end of string
def rm_head_ws(text):
    return text.strip()

def rm_emdash(text):
    # pattern = re.compile('[^\u2014|\u2013]?\s*(.*?)?\s*[\u2014|\u2013]$')
    # pprint(pattern.match(text))
    # return rm_head_ws(re.sub(r'[\u2014|\u2013]?\s*(.*?)?\s*[\u2014|\u2013]', '', text))  # remove em/en dash
    # text = re.sub(r'[\u2014|\u2013]?\s*(.*?)?\s*[\u2014|\u2013]', '', text)
    # text = rm_head_ws(text)
    # text_split = text.split('\n\n')
    # text = ''.join(line for k,line in zip(range(len(text_split)),text_split) if k<len(text_split)-1)
    # return text

    # return rm_head_ws(re.sub(r'[\u2014|\u2013]?\s*[\w?\d]?\s*[\u2014|\u2013]', '', text))  # remove em/en dash
    # remove last line
    # page_index = None
    # for i, l in enumerate(text[::-1]):
    #     if l == '\n':
    #         page_index = i - 1
    #         break
    # if page_index:
    #     text = text[0:len(text) - page_index]
    return text

def find_x0c(text):
    num = []
    for m in re.compile('\x0c').finditer(text):
        num.append(m.start())
    return num

def isEnglish(text):
    text = text.replace(' ', '')
    word = [word for word in text]
    if all(re.match("^[A-Za-z0-9_-]*$",w) for w in word if w not in string.punctuation):
        return True
    else:
        return False
#headings
def isheading(en_text, ch_text):
    if en_text[-1] and ch_text[-1] not in heading_stoppunc: #and all(re.match('[A-Z]', w) for w in text):
        if en_text[-3:] == 'and':
            return False
        else:
            return True
    else:
        return False

# special tokens, e.g., websites, names, etc.., input is the sentence lists
def replace_special_tokens(sent_list):
    # website = 'w{3,}[.]*\w+[.](com)|(org)|(net)|(cn)|(gov)?[.](hk)|(cn)|(tw)'
    website = r'(w){3,}\S+\b'
    prefiex = '(Mr|St|Mrs|Ms|Dr|etc|No)[.]'
    # prefiex = '(Ph.D.|Dr.|Mr.|Mrs.|Ms.|No.)'
    abbre = r'(a[.]m[.]|p[.]m[.]|i[.]e[.]|e[.]g[.]|No[.])'
    item = r'[(]*(i|ii|iii|iv|v|vi|vii|viii)[)]'
    _append = r'(I|II|III|IV|V|VI|VII|VIII)'
    _time = r'\d+(:)+\d+'  # time first
    num = r'[+-]?\d+(?:\.\d+)?'
    num_ = r'[0-9][0-9,.]+'
    hkdollar = r'(HK)\$*(_NUM)'
    perctage = r'(_NUM)\%'
    sents = []
    for sent in sent_list:
        sent = re.sub(website, _TBR, sent)
        sent = re.sub(prefiex, _PREFIXES, sent)
        sent = re.sub(abbre, _ABBRE, sent)
        # sent = re.sub(item, _ITEM, sent)
        sent = re.sub(_time, _NUM, sent)
        sent = re.sub(num_, _NUM, sent)
        sent = re.sub(num, _NUM, sent)
        # sent = re.sub(_append, _NUM, sent)
        sent = re.sub(hkdollar, _HKD, sent)
        sent = re.sub(perctage, _NUM, sent)
        sent = re.sub('[\s]{2,}', ' ', sent)  # double spaceas to single space [important]
        # remove bullets
        sent = re.sub(r'\u2022', '', sent)
        sents.append(sent)
    return sents

def split_par_into_sentence(en_sents, ch_sents): # input is the sentences with token replaced
    if len(en_sents) != len(ch_sents):
        raise Exception('English and Chinese paragraph lengths do not equal')
    en_sent_list, ch_sent_list = [], []
    _stop = r'\.|\?|\!|\。|\！|\？|\:|\;|\：|\；'
    for en_sent, ch_sent in zip(en_sents, ch_sents):
        en_sent = re.sub(_stop, '.<stop>', en_sent).split('<stop>')
        ch_sent = re.sub(_stop, '。<stop>', ch_sent).split('<stop>')

        if len(en_sent) == len(ch_sent):
            en_sent_list.extend(en_sent)
            ch_sent_list.extend(ch_sent)
    # remove empty and num sign
    # en_sent_list = [remove_brackets(sent) for sent in en_sent_list if sent != '' and sent != _NUM+'.']
    # ch_sent_list = [remove_brackets(sent) for sent in ch_sent_list if sent != '' and sent != _NUM+'。']
    en_sent_list = [sent.lower() for sent in en_sent_list if sent != '' and sent != _NUM+'.']  # lower characters
    ch_sent_list = [sent for sent in ch_sent_list if sent != '' and sent != _NUM+'。']
    return en_sent_list, ch_sent_list

def remove_brackets(sent):
    sent_without_bracket, sent_in_bracket = match_brackets(sent)
    return sent_without_bracket


def match_brackets(_sent):
    sent = str(_sent)
    # _left = [m.start(0) for m in re.finditer(r'[\(]|[\（]|\“|\「', sent)]
    # _right = [m.start(0) for m in re.finditer(r'[\)]|[\）]|\”|\」', sent)]
    _left = [m.start(0) for m in re.finditer(r'[\(]|[\（]', sent)]
    _right = [m.start(0) for m in re.finditer(r'[\)]|[\）]', sent)]
    if _right:
        # print([_left, _right])
        sent_in_bracket = []
        sent_without_bracket = sent
        if len(_left) == len(_right):
            _right = allocate_bracket_index(_left, _right)
            for i, _ in enumerate(_left):
                sent_in_bracket.append(sent[_left[i]+1:_right[i]])
                sent_without_bracket = sent_without_bracket.replace(sent[_left[i]:_right[i]+1], '')
        else:
            sent_without_bracket = None
            sent_in_bracket = None
        return sent_without_bracket, sent_in_bracket
    else:
        return _sent, None

def allocate_bracket_index(_left, _right):
    # print([_left, _right])
    _num = len(_left)
    right_index = list(permutations(range(_num-1)))
    _index = []
    for i in range(len(right_index)):
        _index = right_index[i]
        for j, _j in enumerate(_index):
            if _left[j+1] < _right[_j]:
                break
    good_index = []
    for _, i in enumerate(_index):
        good_index.append(_right[i])
    good_index.append(_right[-1])
    return good_index

# text to sentece
def split_into_sentences(text,language):

    if language == '': language = 'en'

    caps = "([A-Z])"
    prefixes = "(Mr|St|Mrs|Ms|Dr|etc|No)[.]"
    suffixes = "(Inc|Ltd|Jr|Sr|Co)"
    starters = "(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
    acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
    digits   = "(\d+)[.](\d+)"
    dotlines = "(\s*[\.]){3,}\s*[\d+]*"   # remove contents dot lines
    website1 = '(w{3})[.]'
    website2 = '[.](com|net|org|io|gov)'
    website3 = '[.](hk|cn)'
    text = " " + text + "  "
    text = text.replace("\n",'')
    text = re.sub(prefixes,"\\1<prd>",text)
    text = re.sub(website1,"\\1<prd>",text)
    text = re.sub(website2,"<prd>\\1", text)
    text = re.sub(website3, "<prd>\\1", text)
    text = re.sub(digits, "\\1<prd>\\2", text)
    text = re.sub(dotlines,'<stop>',text)
    text = re.sub(r'(\b\d{1,2}\b)[.]', '\\1<prd>', text)  # items such as 1., 2.



    if "Ph.D" in text: text = text.replace("Ph.D.","Ph<prd>D<prd>")
    if "a.m." in text: text = text.replace("a.m.", "a<prd>m<prd>")
    if "p.m." in text: text = text.replace("p.m.", "p<prd>m<prd>")
    if "e.g." in text: text = text.replace("e.g.", "e<prd>g<prd>")
    if "i.e." in text: text = text.replace("i.e.", "i<prd>e<prd>")

    text = re.sub("\s" + caps + "[.] "," \\1<prd> ",text)
    text = re.sub(acronyms+" "+starters,"\\1<stop> \\2",text)
    text = re.sub(caps + "[.]" + caps + "[.]" + caps + "[.]","\\1<prd>\\2<prd>\\3<prd>",text)
    text = re.sub(caps + "[.]" + caps + "[.]","\\1<prd>\\2<prd>",text)
    text = re.sub(" "+suffixes+"[.] "+starters," \\1<stop> \\2",text)
    text = re.sub(" "+suffixes+"[.]"," \\1<prd>",text)
    text = re.sub(" " + caps + "[.]"," \\1<prd>",text)


    if language == 'en':
        if "”" in text: text = text.replace(".”","”.")
        if "\"" in text: text = text.replace(".\"","\".")
        if "!" in text: text = text.replace("!\"","\"!")
        if "?" in text: text = text.replace("?\"","\"?")
        text = text.replace(".",".<stop>")
        text = text.replace("?","?<stop>")
        text = text.replace("!","!<stop>")
    elif language == 'ch':
        if "”" in text: text = text.replace("。”","”。")
        if "\"" in text: text = text.replace("。\"","\"。")
        if "！" in text: text = text.replace("！\"","\"！")
        if "？" in text: text = text.replace("？\"","\"？")
        text = text.replace("。","。<stop>")
        text = text.replace("？","？<stop>")
        text = text.replace("！","！<stop>")

    text = text.replace("<prd>",".")
    sentences = text.split("<stop>")
    sentences = sentences[:-1]
    sentences = [s.strip() for s in sentences]
    # remove page index
    # pprint(sentences[-1])
    # if u'\u2013' in sentences[-1] or u'\u2014' in sentences[-1]:
    #     pprint("yes")
    #     sentences = sentences[0:-2]
    # else:
    #     pprint("no")
    return sentences

def word_count(sent,languabe='en'):
    if languabe == 'en':
        #word = nltk.word_tokenize(re.sub(r'\.|\,|\?','',sent))
        pass
    elif languabe == 'ch':
        word = list(jieba.cut(sent, cut_all=False))
    else:
        word = None
    return len(word)

def split_raw_paragraph(text, replace=False):
    #split raw text into paragraphs
    #return: list of paragraphs
    # remove brackets
    en_brackets = r'\(([^()]+)\)'
    ch_brackets = r'\（([^（）]+)\）'
    for _ in range(3):
        text = re.sub(en_brackets, '', text)
        text = re.sub(ch_brackets, '', text)
    text = text.replace('\n\n', '<par>')
    text = text.replace('\n', ' ')  # replace line break with space
    # text = re.sub('[.]{2,}', '.', text)
    text = text.split('<par>')
    if replace == True:
        text = [s.strip() for s in text if s != '']  # remove empty lines
    else:
        text = [s.strip() for s in text]
    return text

def split_paragraph_sentences(text):
    stoppunc = ['.', '?', "!"]
    sentences = [sent + '.' for sent in text if sent[-1] not in stoppunc]
    return sentences

def _pairParSentence(en_par, ch_par):
    #if len(en_par) != len(ch_par):
    #    raise Exception('Paragraph size not equal')
    en_pair_sent, ch_pair_sent, en_pair_heading, ch_pair_heading = [], [], [], []
    for en_sent, ch_sent in zip(en_par, ch_par):
        if en_sent and ch_sent:
            if isheading(en_sent, ch_sent):
                en_pair_heading.append(en_sent)
                ch_pair_heading.append(ch_sent)
            else:
                en_pair_sent.append(en_sent)
                ch_pair_sent.append(ch_sent)
    return en_pair_sent, ch_pair_sent, en_pair_heading, ch_pair_heading


def pairParSentene(en_text, ch_text):
    # get both para
    en_par = split_raw_paragraph(en_text)
    ch_par = split_raw_paragraph(ch_text)
    # first check of number of paragraph
    if len(en_par) != len(ch_par):
        en_par = split_raw_paragraph(en_text, True)
        ch_par = split_raw_paragraph(ch_text, True)
    # second check
    #don't check for the time being
    if len(en_par) == len(ch_par):
        same_num = True
    else:
        same_num = False
    return _pairParSentence(en_par, ch_par), same_num
    # if len(en_par) == len(ch_par):
    #     return _pairParSentence(en_par, ch_par)
    # else:
    #     return [None]*4

def sentence_tokenize(sent, language='en'):
    if language=='en':
        #words = list(nltk.word_tokenize(sent))\
        words = sent.split(' ')
    else:
        sent = sent.replace(' ', '')
        words = list(jieba.cut(sent, cut_all=False))
    return ' '.join(words).strip()


class intoPairSentenes(object):
    def __init__(self, en_text, ch_text):
        self.en_text = en_text
        self.ch_text = ch_text
        self.en_par = split_raw_paragraph(en_text)
        self.ch_par = split_raw_paragraph(ch_text)
        (self.en_pair_sent, self.ch_pair_sent, self.en_pair_heading, self.ch_pair_heading), self.same_num = pairParSentene(en_text, ch_text)
        if self.en_pair_sent and self.ch_text:
            self.en_pair_sent = replace_special_tokens(self.en_pair_sent)
            self.ch_pair_sent = replace_special_tokens(self.ch_pair_sent)
            self.en_pair_sent, self.ch_pair_sent = split_par_into_sentence(self.en_pair_sent, self.ch_pair_sent)



class myPage:
    def __init__(self,file_name):
        self.text = open(file_name, 'rt', encoding='utf-8').read()
        self.page_index = find_x0c(self.text)
        self.page_nums = len(self.page_index)
        self.file_name = file_name

    def get_raw_page(self,page_num):
        if page_num>self.page_nums-1:
            logging.info('Out of page range')
            return ""
        if page_num == 0:
            return self.text[:self.page_index[0]]
        else:
            return self.text[self.page_index[page_num-1]:self.page_index[page_num]-1]

    def get_title(self,page_num):
        # if language not in ['en','ch']: logging.info('Please choose language: en/ch')
        if page_num == 0:
            title = 'NA'
            isTitle = False
        else:
            text = self.text[self.page_index[page_num - 1]:self.page_index[page_num] - 1]
            text = text.split('\n\n')[0]
            text = text[1:].replace('\n', ' ')  # find titles
            text = re.sub(r'\s{3,}', '', text)  # replace long whitespaces
            text = text.strip()
            if isEnglish(text):
                if text.isupper():
                    title = text
                    isTitle = True
                else:
                    title = 'NA'
                    isTitle = False
            else:
                title = text
                isTitle = None
        return title,isTitle

    def get_page(self,page_num):
        if page_num>self.page_nums-1:
            logging.info('Out of page range')
            return ""
        if page_num == 0:
            return self.text[:self.page_index[0]].strip()
        else:
            return self.text[self.page_index[page_num-1]+1:self.page_index[page_num]-1].strip()

    def get_clean_page(self,page_num):
        text = rm_emdash(self.get_page(page_num))
        text = re.sub(r'\s{3,}', '', text)
        return text

class myPairPage:
    def __init__(self,en_file,ch_file):
        self.enPage = myPage(en_file)
        self.chPage = myPage(ch_file)
        self.enText = re.sub(r'\n{2}','.',self.enPage.text)
        self.chText = re.sub(r'\n{2}','。',self.chPage.text)
        self.enText = re.sub(r'\.{2,}','.',self.enText)   # replace double lines
        self.chText = re.sub(r'\。{2,}','。',self.chText)
        # self.enText = self.enPage.text.replace(r'\n{2}','.')
        # self.chText = self.chPage.text.replace(r'\n{2}','。')
        self.enPage_index = find_x0c(self.enText)
        self.chPage_index = find_x0c(self.chText)
        self.Page_nums = min(len(self.enPage_index),len(self.chPage_index))

    def get_clean_pages(self,page_num):
        if page_num == 0:
            enPage_content = self.enText[:self.enPage_index[0]]
            chPage_content = self.chText[:self.chPage_index[0]]
        else:
            enPage_content = self.enText[self.enPage_index[page_num - 1] + 1:self.enPage_index[page_num] - 1]
            chPage_content = self.chText[self.chPage_index[page_num - 1] + 1:self.chPage_index[page_num] - 1]

        enPage_content = rm_emdash(enPage_content)
        enPage_content = re.sub(r'\s{3,}', '', enPage_content)
        chPage_content = rm_emdash(chPage_content)
        chPage_content = re.sub(r'\s{3,}', '', chPage_content)
        return enPage_content, chPage_content

    def get_senteces(self,page_num):
        en_page, ch_page = self.get_clean_pages(page_num)
        en_sent = split_into_sentences(en_page,'en')
        ch_sent = split_into_sentences(ch_page,'ch')
        # en_sent = [re.sub(r'\s+','',w) for w in en_sent]
        ch_sent = [re.sub(r'\s+','',w) for w in ch_sent]
        # get rid of puncuations
        return en_sent, ch_sent

    def get_title(self,page_num):
        en_title, isen_title = self.enPage.get_title(page_num)
        if isen_title:
            ch_title, __ = self.chPage.get_title(page_num)
            return en_title, ch_title
        else:
            return None, None
    # remove titles
    def adj_sentences(self,page_num):
        en_sent, ch_sent = self.get_senteces(page_num)
        ch_sent_adj = [None]*len(en_sent)
        if len(ch_sent)-len(en_sent) == 1:
            try:
                enSent_len = [word_count(w,'en') for w in en_sent]
                chSent_len = [word_count(w,'ch') for w in ch_sent]

                # find possible index
                ia = [enSent_len.index(x) for x in sorted(enSent_len, reverse=True)]
                ib = [chSent_len.index(x) for x in sorted(chSent_len, reverse=True)]

                index_sum = []
                for i in range(3): # only first three long sentences
                    index_ = ib.index(ia[i]) + ib.index(ia[i]+1)
                    index_sum.append(index_)
                max_index = ia[index_sum.index(max(index_sum))]

                ch_sent_adj[:max_index] = ch_sent[:max_index]
                ch_sent_adj[max_index] = ch_sent[max_index] + ch_sent[max_index+1]
                ch_sent_adj[max_index+1:] = ch_sent[max_index+2:]
            except:
                ch_sent_adj = ch_sent

        else:
            ch_sent_adj = ch_sent

        en_title, ch_title = self.get_title(page_num)
        if en_title and ch_title:
            en_sent = en_sent[1:]
            ch_sent_adj = ch_sent_adj[1:]
        return en_sent, ch_sent_adj


class myPairFile:
    def __init__(self,en_path='en_ipo_files_converted',ch_path='ch_ipo_files_converted'):
        en_file_list = os.listdir('./'+en_path)
        ch_file_list = os.listdir('./'+ch_path)
        self.pair_file = [w for w in ch_file_list if w in en_file_list]
        self.len_pair_file = len(self.pair_file)


def pair(en_path, ch_path, en_save_path, ch_save_path):
    data_path = [en_path, ch_path, en_save_path, ch_save_path]
    for path in data_path:
        if not os.path.isdir(path):
            os.mkdir(path)
        
    file_list = os.listdir(en_path)

    for file in file_list:

        filename = file
        file1 = en_path + '/' + filename
        file2 = ch_path + '/' + filename
        ipo_page = myPairPage(file1,file2)
        TotalPages = ipo_page.Page_nums

        enPairSentPath = './' + en_save_path + '/' + str(filename) + '_enPairSent.txt'
        chPairSentPath = './' + ch_save_path + '/' + str(filename) + '_chPairSent.txt'
        """
        enNotPairSentPath = './' + data_path + '/' + str(filename)[:-4] + '_enNotPairSent.txt'
        chNotPairSentPath = './' + data_path + '/' + str(filename)[:-4] + '_chNotPairSent.txt'
        """
        container = []
        enSent_fw = open(enPairSentPath, 'a', encoding='utf-8')
        chSent_fw = open(chPairSentPath, 'a', encoding='utf-8')

        for page_num in range(TotalPages):
            en_page = myPage(file1)
            ch_page = myPage(file2)

            raw_en_text = en_page.get_raw_page(page_num)
            raw_ch_text = ch_page.get_raw_page(page_num)

            en_text = en_page.get_page(page_num)
            ch_text = ch_page.get_page(page_num)

            pairSent = intoPairSentenes(en_text, ch_text)
            if (pairSent.en_pair_sent is not None) and (pairSent.ch_pair_sent is not None):
                #check whether the sentences are completely paired
                if pairSent.same_num:                
                    # write to file
                    for en_line, ch_line in zip(pairSent.en_pair_sent, pairSent.ch_pair_sent):
                        #write sentence
                        enSent_fw.write(sentence_tokenize(en_line) + '\n')
                        chSent_fw.write(sentence_tokenize(ch_line, language='ch') + '\n')

                else:
                    container.append((pairSent.en_pair_sent, pairSent.ch_pair_sent))
            else:
                pass
        """
        enSent_fw = open(enNotPairSentPath, 'a', encoding='utf-8')
        chSent_fw = open(chNotPairSentPath, 'a', encoding='utf-8')
        for en_pair, ch_pair in container:
            for en_line, ch_line in zip(en_pair, ch_pair):
                enSent_fw.write(sentence_tokenize(en_line) + '\n')
                chSent_fw.write(sentence_tokenize(ch_line, language='ch') + '\n')
                """

        print('write finish!')