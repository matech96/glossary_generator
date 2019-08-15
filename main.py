import os

import PyPDF2
import re
from collections import defaultdict
import time

from pdfquery.cache import FileCache

from PreallocatedList import PreallocatedList
import pdfquery
import unidecode
import codecs
import configparser
import multiprocessing as mp
import gc


def fnPDF_FindText(pdfDoc, words, offset):
    # xfile : the PDF file in which to look
    # xString : the string to look for
    print(str(0) + '%')
    res = defaultdict(lambda: PreallocatedList(100, int))
    num_pages = pdfDoc.getNumPages()
    prev_prc = 0
    for i in range(0, num_pages):
        content = unidecode.unidecode(pdfDoc.getPage(i).extractText()).lower()
        content = re.sub(r'\s+', ' ', content)
        for word in words:
            if unidecode.unidecode(word).lower() in content:
                res[word].append(i + offset)
        prc = (i * 100.0) / num_pages
        if prc > (prev_prc + 1) * 25:
            prev_prc += 1
            print(str(prev_prc * 25) + '%')
    return res


def pdfquery_FindText(filenamme, words, offset):
    # xfile : the PDF file in which to look
    # xString : the string to look for

    start_time = time.time()
    querys = [f'LTTextLineHorizontal:contains("{word}")' for word in words]
    res = defaultdict(lambda: PreallocatedList(1000, int))
    pdf = pdfquery.PDFQuery(filenamme, parse_tree_cacher=FileCache("tmp/"))
    page_num = 0
    while True:
        try:
            pdf.load(page_num)
            query_objs = [pdf.pq(query) for query in querys]
            for query_obj, word in zip(query_objs, words):
                if query_obj:
                    res[word].append(page_num + offset)
            page_num += 1
            if page_num % 30 == 0:
                del pdf
                collected = gc.collect()
                print(f"Garbage collector: collected {collected} objects.")
                pdf = pdfquery.PDFQuery(filenamme, parse_tree_cacher=FileCache("tmp/"))
                # if page_num % 100 == 0:
                print(page_num)
            # break
        except StopIteration:
            break
    print("--- Batch futási idő: %s másodperc ---" % (time.time() - start_time))
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
    os.makedirs('tmp', exist_ok=True)
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

    print(f'Number of words: {len(words)}')
    pool = mp.Pool(4)
    batch = []
    for word in words:
        batch.append(word)
        if len(batch) == 5:
            # process_word_batch(filename, offset, words)
            pool.apply_async(process_word_batch, (filename, offset, batch))
            batch = []
    # process_word_batch(filename, offset, words)
    pool.apply_async(process_word_batch, (filename, offset, batch))
    print('-----')
    pool.close()
    pool.join()
    # process_word_batch(filename, offset, words)


def process_word_batch(filename, offset, words):
    pdf_query = True
    if not pdf_query:
        pdfFileObj = open(filename, 'rb')
        pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
        results = fnPDF_FindText(pdfReader, words, offset)
        pdfFileObj.close()
    else:
        results = pdfquery_FindText(filename, words, offset)
    # return results
    with open('results.txt', 'a') as f:
        for k in results:
            pages = sorted(results[k].tolist())
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
