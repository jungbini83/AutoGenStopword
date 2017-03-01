# -*- encoding:utf-8-*-
import os, re, string, operator
from collections import Counter
from nltk.corpus import stopwords
from collections import defaultdict
from nltk import word_tokenize
# from porter2stemmer import Porter2Stemmer

CUR_PATH = os.getcwd()
INPUT_PATH = CUR_PATH + '/parsedData/'
TRAIN_COMMIT_PATH = INPUT_PATH + 'Commits/train/'
TEST_COMMIT_PATH = INPUT_PATH + 'Commits/test/'
TRAIN_NLP_PATH = INPUT_PATH + 'TrainCommits/'
TEST_NLP_PATH = INPUT_PATH + 'TestCommits/'

# stemmer = Porter2Stemmer()

def is_number(s):
    try:
        float(s) if '.' in s else int(s)
        return True
    except ValueError:
        return False

def separate_words(text, min_word_return_size):
    """
    Utility function to return a list of all words that are have a length greater than a specified number of characters.
    @param text The text that must be split in to words.
    @param min_word_return_size The minimum no of characters a word must have to be included.
    """
    splitter = re.compile('[^a-zA-Z0-9_\\+]')
    words = []
    for single_word in splitter.split(text):
        current_word = single_word.strip().lower()
        #leave numbers in phrase, but don't count as words, since they tend to invalidate scores of their phrases
        if len(current_word) > min_word_return_size and current_word != '' and not is_number(current_word):
            words.append(current_word)
    return words

def splitWords(WordList):
    
    newWordList = []
    for wordItem in WordList:
        tmpList1 = re.findall('[A-Z]*[a-z]+', wordItem)                 # �빮�ڷ� �����ϴ� �ռ��� (e.g. Ŭ���� ��)        
        if tmpList1:
            newWordList += tmpList1
        else:
            newWordList.append(wordItem)
        
    return newWordList                 

def writeTermFrequency(counter):
    
    OUTPUT_PATH = CUR_PATH + '/TermFrequency/'
    if not os.path.exists(OUTPUT_PATH):
            os.makedirs(OUTPUT_PATH)
    
    OUTPUT_FILE = open(OUTPUT_PATH + 'TermFreq.txt', 'w')
    
    for k, v in counter.items():
        OUTPUT_FILE.write(k + '|' + str(v) + '\n')
        
    OUTPUT_FILE.close()
        
def writeCoOccurenceFreq(matrix):
    
    OUTPUT_PATH = CUR_PATH + '/TermFrequency/'
    if not os.path.exists(OUTPUT_PATH):
            os.makedirs(OUTPUT_PATH)
    
    OUTPUT_FILE = open(OUTPUT_PATH + 'CoOccurenceFreq.txt', 'w')
    
    for w1 in matrix:
        
        for w2, w2_count in matrix[w1].items():            
            OUTPUT_FILE.write(w1 + '|' + w2 + '|' + str(w2_count) + '\n')
    
    OUTPUT_FILE.close()
    
def writeTotalDocNum(totalNum):
    
    OUTPUT_PATH = CUR_PATH + '/TermFrequency/'
    if not os.path.exists(OUTPUT_PATH):
            os.makedirs(OUTPUT_PATH)
    
    OUTPUT_FILE = open(OUTPUT_PATH + 'TotalDocNum.txt', 'w')
    OUTPUT_FILE.write(str(totalNum))
    OUTPUT_FILE.close()    
        
def printMostCoOccurence(matrix, n):
    
    com_max = []
    for w1 in matrix:
        w1_max_terms = sorted(matrix[w1].items(), key=operator.itemgetter(1), reverse=True)[:n]
        for w2, w2_count in w1_max_terms:
            com_max.append(((w1, w2), w2_count))
        
    terms_max = sorted(com_max, key=operator.itemgetter(1), reverse=True)
    print terms_max[:n]
        
def calcuateDocFrequency():
    
    FOX_OUTPUT_FILE = open(CUR_PATH + '/TermFrequency/DocFreq(fox).txt', 'w')
    ALL_OUTPUT_FILE=  open(CUR_PATH + '/TermFrequency/DocFreq(all).txt', 'w')
    
    FOX_STOPWORD_LIST = [line.strip() for line in open(CUR_PATH + '/mallet/stoplists/fox_stopwords.txt', 'r')]
            
    docList = [line for line in open(TRAIN_NLP_PATH + '/commits(train).txt', 'r')]
    
    # Fox stop words 안에 있는 term만 doc freq 저장
    termList_fox = list()    
    for document in docList:
        token = document.split()
        
        tmpDict = {}
        for term in token:
            if term in FOX_STOPWORD_LIST:
                tmpDict.setdefault(term, 0)
                tmpDict[term] += 1
        
        termList_fox.append(tmpDict)
    
    docFreq_fox = Counter()
    map(docFreq_fox.update, (termFreq.keys() for termFreq in termList_fox))
    
    for termName, count in docFreq_fox.items():
        FOX_OUTPUT_FILE.write(termName + '|' + str(count) + '\n')
        
    # 모든 training set 의 term의 doc freq 저장
    termList_all = [Counter(doc.split()) for doc in docList]
    
    docFreq_all = Counter()
    map(docFreq_all.update, (termFreq.keys() for termFreq in termList_all))
    
    for termName, count in docFreq_all.items():
        ALL_OUTPUT_FILE.write(termName + '|' + str(count) + '\n')

def preprocess_train(PROJECT_LIST):
            
    count_all = Counter()                                                   # 단어 빈도수 계산을 위한 클래
    co_occur_matrix = defaultdict(lambda: defaultdict(int))                 # 동시 발생 갯수를 저장할 메트릭스
    
    if not os.path.exists(TRAIN_NLP_PATH):
        os.makedirs(TRAIN_NLP_PATH)
    
    TRAIN_ALL_FILE = open(TRAIN_NLP_PATH + '/commits(train).txt', 'w')                # 모든 프로젝트의 commit 메시지를 저장
    
    total_doc_num = 0
    for program in PROJECT_LIST:
        
        print 'preprocessing ' + program + '...' 
        
        OUTPUT_PATH = TRAIN_NLP_PATH + program
        if not os.path.exists(OUTPUT_PATH):
            os.makedirs(OUTPUT_PATH)
            
        MERGE_FILE = open(TRAIN_NLP_PATH + '/' + program + '.txt', 'w')
        
        total_program_doc_num = 0
        for path, dir, files in os.walk(TRAIN_COMMIT_PATH + program):
            
            for filename in files:
                
                # 자연어 전처리 과정
                doc_raw             = open(path + '/' + filename, 'r').read()                
#                 doc_letters_only    = re.sub('[^a-zA-Z]', ' ', doc_raw)             # 알파벳만 가져오기
#                 doc_token           = word_tokenize(doc_letters_only)
#                 doc_split_word      = splitWords(doc_token)
#                 doc_stemmed         = [stemmer.stem(w) for w in doc_split_word]
#                 doc_remove_dup      = list(set(doc_stemmed))
#                 doc_len_check       = [w for w in doc_remove_dup if len(w) > 2]
                doc_token           = separate_words(doc_raw, 2)
                doc_lower           = [w.lower() for w in doc_token]
                                                
                if len(doc_lower) != 0:
                    
                    total_program_doc_num += 1
                    
                    OUTPUT_FILE = open(OUTPUT_PATH + '/' + filename, 'w')
                    OUTPUT_FILE.write(' '.join(doc_lower))
                    MERGE_FILE.write(' '.join(doc_lower) + '\n')
                    TRAIN_ALL_FILE.write(' '.join(doc_lower) + '\n')                    
                    OUTPUT_FILE.close()
                    
                    count_all.update(doc_lower)                             # count terms
                    
                    for i in range(len(doc_lower) - 1):
                        for j in range(i+1, len(doc_lower)):
                            w1, w2 = sorted([doc_lower[i].lower(), doc_lower[j].lower()])
                            if w1 != w2:
                                co_occur_matrix[w1][w2] += 1
                                
        MERGE_FILE.close()
        
        print 'The number of doc of ' + program + ' is ' + str(total_program_doc_num)
        total_doc_num += total_program_doc_num 
        
    writeTermFrequency(count_all)                                   # 전체 단어 빈도수 저장하기
    writeCoOccurenceFreq(co_occur_matrix)                           # 동시 발생 단어 빈도수 저장하기
    writeTotalDocNum(total_doc_num)                                 # 전체 커밋 문서(doc)의 갯수를 저장
    
def preprocess_test(PROJECT_LIST):
    
    if not os.path.exists(TEST_NLP_PATH):
        os.makedirs(TEST_NLP_PATH)
    
    for program in PROJECT_LIST:
        
        print 'preprocessing ' + program + '...' 
        
        OUTPUT_PATH = TEST_NLP_PATH + program
        if not os.path.exists(OUTPUT_PATH):
            os.makedirs(OUTPUT_PATH)
                    
        for path, dir, files in os.walk(TEST_COMMIT_PATH + program):
            
            for filename in files:
                
                tokenizedLine = list()
                # 자연어 전처리 과정
                doc_raw             = open(path + '/' + filename, 'r').read()                
#                 doc_letters_only    = re.sub('[^a-zA-Z]', ' ', doc_raw)             # 알파벳만 가져오기
#                 doc_token           = word_tokenize(doc_letters_only)
#                 doc_split_word      = splitWords(doc_token)
#                 doc_stemmed         = [stemmer.stem(w) for w in doc_split_word]
#                 doc_remove_dup      = list(set(doc_stemmed))
#                 doc_len_check       = [w for w in doc_remove_dup if len(w) > 2]
                doc_token           = separate_words(doc_raw, 2)
                doc_lower           = [w.lower() for w in doc_token] 
                    
                if len(doc_lower) != 0:                        
                    OUTPUT_FILE = open(OUTPUT_PATH + '/' + filename, 'w')
                    OUTPUT_FILE.write(' '.join(doc_lower))
                    OUTPUT_FILE.close()    
    
if __name__ == "__main__":
    
    PROJECT_LIST = ['kotlin','gradle','orientdb','PDE','Actor','hadoop','Graylog','cassandra','CoreNLP','netty','druid','alluxio']
    
#     preprocess_train(PROJECT_LIST)
#     preprocess_test(PROJECT_LIST)
    calcuateDocFrequency()
    
    