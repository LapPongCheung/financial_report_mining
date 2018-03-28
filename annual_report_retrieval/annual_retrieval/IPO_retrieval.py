# -*- coding: utf-8 -*-

import urllib.request
from bs4 import BeautifulSoup
import datetime
import os
from random import randint
from time import sleep
import json
import pickle

en_url = r"http://www.hkexnews.hk/listedco/listconews/advancedsearch/search_active_main.aspx"
ch_url = r"http://www.hkexnews.hk/listedco/listconews/advancedsearch/search_active_main_c.aspx"

domain = r"http://www.hkexnews.hk/"

def paras_viewstate(soup):
    dic = {}
    dic['__VIEWSTATE'] = soup.find("input", {"type": "hidden", "name": "__VIEWSTATE"})['value']
    dic['__VIEWSTATEGENERATOR'] = soup.find("input", {"type": "hidden", "name": "__VIEWSTATEGENERATOR"})['value']
    dic['__VIEWSTATEENCRYPTED'] = soup.find("input", {"type": "hidden", "name": "__VIEWSTATEENCRYPTED"})['value']
    return dic

def paras_setting(dic, keyword, start_date, end_date, type_of_doc):
    dic['ctl00$txt_today']='20170919'
    dic['ctl00$hfStatus']='AEM'
    dic['ctl00$hfAlert']=''
    dic['ctl00$txt_stock_name']=''
    dic['ctl00$rdo_SelectDocType']='rbAll'
    
    dic['ctl00$rdo_SelectDateOfRelease']='rbManualRange'
    dic['ctl00$sel_DateOfReleaseFrom_d']= str(start_date.day)
    dic['ctl00$sel_DateOfReleaseFrom_m']= '{:02d}'.format(start_date.month)
    dic['ctl00$sel_DateOfReleaseFrom_y']= str(start_date.year)
    dic['ctl00$sel_DateOfReleaseTo_d']= str(end_date.day)
    dic['ctl00$sel_DateOfReleaseTo_m']= '{:02d}'.format(end_date.month)
    dic['ctl00$sel_DateOfReleaseTo_y']= str(end_date.year)
    dic['ctl00$sel_defaultDateRange']='SevenDays'
    dic['ctl00$rdo_SelectSortBy']='rbDateTime'
    if type_of_doc == 'ipo':
        dic['ctl00$sel_tier_1']='3'
        dic['ctl00$sel_DocTypePrior2006']='-1'
        #sub-types of documents
        dic['ctl00$sel_tier_2_group']=''
        dic['ctl00$sel_tier_2']='153'
        
        #dic['ctl00$ddlTierTwo']='153,3,-1'
        dic['ctl00$ddlTierTwo']=''
        dic['ctl00$ddlTierTwoGroup']=''
        dic['ctl00$txtKeyWord']= keyword

    elif type_of_doc == 'annual_report':
        dic['ctl00$sel_tier_1']='4'
        dic['ctl00$sel_DocTypePrior2006']='-1'
        dic['ctl00$sel_tier_2_group']='-2'
        dic['ctl00$sel_tier_2']='-2'        
        dic['ctl00$ddlTierTwo']='176,5,22'
        dic['ctl00$ddlTierTwoGroup']='22,5'
        dic['ctl00$txtKeyWord']=''
    else:
        raise Exception('please specify which type of doc you are going to download')
    return dic

def get_links(url, paras):
    data = urllib.parse.urlencode(paras).encode('ascii')
    req = urllib.request.Request(url, data)

    response = urllib.request.urlopen(req)
    soup = BeautifulSoup(response.read(),"lxml")

    #get the pdf links
    """
    pdfs = soup.findAll('a', {'class': 'news'})
    tags = soup.findAll('span')
    tags = [tag for tag in tags if 'id' in tag.attrs]
    codes = [code.contents[0] for code in tags if 'StockCode' in code['id']]
    pdfs = [pdf['href'] for pdf in pdfs if pdf['href'][-4:] == '.pdf']
    if len(pdfs) != len(codes) - 1:
        print (pdfs, codes)
    return zip(pdfs, codes[1:])
    """
    table = soup.find("table", {'id':"ctl00_gvMain"})
    links = []
    codes = []
    for tr in table.findAll('tr'):
        try:
            tag = tr.find('a', {'class': 'news'})
            if tag['href'][-4:] == '.pdf':
                link = tag['href']
                code = [span for span in tr.findAll('span') if 'StockCode' in span['id']][0]
                links.append(link)
                codes.append(code.contents[0])
        except:
            pass
    
    return zip(links, codes)

def download(ch_save_path, en_save_path, start_date, end_date, type_of_doc):

    if os.path.exists("download_record.pkl"):
        records = pickle.load(open("download_record.pkl", 'rb'))
    else:
        records = {'dates':set()}
    
    timedelta = datetime.timedelta(days = 7)
    ch_links = []
    en_links = []
    date_ch_links = []
    date_en_links = []

    #check whether the documents are already downloaded
    date_range = end_date - start_date
    dates = set([start_date + datetime.timedelta(days = i) for i in range(date_range.days + 1)])
    not_yet_download = dates - records['dates']

    print (not_yet_download)

    
    for date in not_yet_download:
        #get ch links
        for link_container, temp_container, url, keywords in zip([ch_links, en_links], [date_ch_links, date_en_links], [ch_url, en_url], [[u'發售'], ['offer']]):
    
            with urllib.request.urlopen(url) as web:
                soup = BeautifulSoup(web.read(),"lxml")    
            #form data
            
            for keyword in keywords:
                fd = paras_viewstate(soup) 
                fd = paras_setting(fd, keyword, date, date + datetime.timedelta(days = 1), type_of_doc)
                temp_container = get_links(url, fd)
                link_container.extend(temp_container)

            sleep(randint(10, 100)/100)

        records[date] = {'ch':date_ch_links, 'en': date_en_links}
        date_ch_links = []
        date_en_links = []

    records['dates'] = records['dates'] | dates
                

    for directory in [ch_save_path, en_save_path]:
    	if not os.path.exists(directory):
    	    os.makedirs(directory)

    ch_docs = os.listdir(ch_save_path)
    en_docs = os.listdir(en_save_path)

    print ("going to download: ", ch_links)
    
    for link in ch_links:
        code = link[1]
        link = link[0]
        if code + '.pdf' in ch_docs:
            continue
        else:
            d = urllib.request.urlopen(domain+link)
            #if int(d.info()['Content-Length'])> 2000000:
            urllib.request.urlretrieve (domain+link, os.path.join(ch_save_path, code + '.pdf'))
            print (code)
            sleep(randint(10, 100)/100)
    
    for link in en_links:
        code = link[1]
        link = link[0]
        if code + '.pdf' in en_docs:
            continue
        else:
            d = urllib.request.urlopen(domain+link)
            #if int(d.info()['Content-Length'])> 2000000:
            urllib.request.urlretrieve (domain+link, os.path.join(en_save_path, code + '.pdf'))
            print (code)
            sleep(randint(10, 100)/100)

    with open("download_record.pkl", 'wb') as fp:
        pickle.dump(records, fp)

            








