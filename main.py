import PyPDF2
import re
from collections import defaultdict
import time

import pdfquery
import unidecode
import codecs
import configparser
import os
from multiprocessing import Pool

def fnPDF_FindText(pdfDoc, words, offset):
    # xfile : the PDF file in which to look
    # xString : the string to look for
    print(str(0) + '%')
    res = defaultdict(lambda: set())
    num_pages = pdfDoc.getNumPages()
    prev_prc = 0
    for i in range(0, num_pages):
        content = unidecode.unidecode(pdfDoc.getPage(i).extractText()).lower()
        content = re.sub(r'\s+', ' ', content)
        for word in words:
            if unidecode.unidecode(word).lower() in content:
                res[word].add(i + offset)
        prc = (i*100.0)/num_pages
        if prc > (prev_prc + 1) * 25:
            prev_prc += 1
            print(str(prev_prc*25) + '%')
    return res


def pdfquery_FindText(filenamme, words, offset):
    # xfile : the PDF file in which to look
    # xString : the string to look for
    res = defaultdict(lambda: [None]*100)
    pdf = pdfquery.PDFQuery(filenamme)
    page_num = 0
    p = Pool(4)
    while True:
        try:
            pdf.load(page_num)
            res = p.map(lambda word: pdf.pq(f'LTTextLineHorizontal:contains("{word}")'), words)
            for r, word in zip(res, words):
                if r:
                    res[word].add(page_num + offset)
            page_num += 1
            if page_num % 100 == 0:
                print(page_num)
        except StopIteration:
            break
    return res

def raw_index_reader():
    words = []
    end = True
    with open('index.txt', encoding='UTF-8') as f:
        for line in f:
            if end:
                for match in re.finditer(r'^(\w+\s*)+', line):
                    m = match.group(0)
                    words.append(m)
            end = line[-2] != ' '
    return words

def clean_index_reader():
    words = []
    with open('index.txt', encoding='UTF-8') as f:
        for line in f:
            words.append(line.strip())
    return words

def main():
    config = configparser.ConfigParser(inline_comment_prefixes=('#', ';'))
    config.read_file(codecs.open("config.txt", "r", "utf8"))    
    section = config['PDF']
    filename = section['PDFFileName']
    offset = int(section['Offest'])

    clean_index = True
    if not clean_index:
        words = raw_index_reader()
    else:
        words = clean_index_reader()

    print('-----')
    pdf_query = True
    if not pdf_query:
        pdfFileObj = open(filename, 'rb')
        pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
        results = fnPDF_FindText(pdfReader, words, offset)
        pdfFileObj.close()
    else:
        results = pdfquery_FindText(filename, words, offset)
    with open('results.txt', 'w') as f:
        for k in results:
            pages = sorted(list(results[k]))
            if len(pages) != 0:
                f.write(k + ': ')
                first_page = -1
                last_page = -1
                for page in pages:
                    if page != last_page + 1:
                        print_pages(f, first_page, last_page)
                        f.write(', ')
                        first_page = page
                    last_page = page
                print_pages(f, first_page, last_page)
                f.write('\n')


def print_pages(f, first_page, last_page):
    if first_page > 0:
        if last_page != first_page:
            page_str = str(first_page) + '-' + str(last_page)
            f.write(page_str)
        else:
            page_str = str(first_page)
            f.write(page_str)
        # print(page_str)


if __name__ == '__main__':
    start_time = time.time()
    main()
    print("--- Futási idő: %s másodperc ---" % (time.time() - start_time))