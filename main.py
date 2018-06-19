import PyPDF2
import re
from collections import defaultdict
import time


def fnPDF_FindText(pdfDoc, words):
    # xfile : the PDF file in which to look
    # xString : the string to look for
    print(str(0) + '%')
    res = defaultdict(lambda: set())
    num_pages = pdfDoc.getNumPages()
    prev_prc = 0
    for i in range(0, num_pages):
        content = ""
        content += pdfDoc.getPage(i).extractText()
        content = re.sub(r'\s+', ' ', content)
        for word in words:
            if word in content:
                res[word].add(i + 1)
        prc = (i*100.0)/num_pages
        if prc > (prev_prc + 1) * 25:
            prev_prc += 1
            print(str(prev_prc*25) + '%')
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
            pages = sorted(list(results[k]))
            if len(pages) != 0:
                f.write(k + ', ' + ', '.join(map(str, pages)) + '\n')


if __name__ == '__main__':
    start_time = time.time()
    main()
    print("--- Futási idő: %s másodperc ---" % (time.time() - start_time))
