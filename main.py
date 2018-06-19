import PyPDF2
import re
from collections import defaultdict
import time


def fnPDF_FindText(pdfDoc, words):
    # xfile : the PDF file in which to look
    # xString : the string to look for
    res = defaultdict(lambda: set())
    for i in range(0, pdfDoc.getNumPages()):
        content = ""
        content += pdfDoc.getPage(i).extractText()
        for word in words:
            if word in content:
                res[word].add(i + 1)
        print(i)
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
    end = True
    with open('index.txt', encoding='UTF-8') as f:
        for line in f:
            words.append(line.strip())
    return words

def main():
    clean_index = True
    words = []
    if not clean_index:
        words = raw_index_reader()
    else:
        words = clean_index_reader()

    print(len(words))
    print('-----')
    pdfFileObj = open('Deng_06-14.pdf', 'rb')
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
    results = fnPDF_FindText(pdfReader, words)
    pdfFileObj.close()
    with open('results.txt', 'w') as f:
        for k in results:
            pages = results[k]
            if len(pages) != 0:
                f.write(k + ', ' + ', '.join(map(str, pages)) + '\n')


if __name__ == '__main__':
    start_time = time.time()
    main()
    print("--- Futási idő: %s másodperc ---" % (time.time() - start_time))
