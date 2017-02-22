# -*- encoding:utf-8-*-
import os, re, string, operator
from collections import Counter
from nltk.corpus import stopwords
from collections import defaultdict

CUR_PATH = os.getcwd()
INPUT_PATH = CUR_PATH + '/parsedData/'
TRAIN_COMMIT_PATH = INPUT_PATH + 'Commits/train/'
TEST_COMMIT_PATH = INPUT_PATH + 'Commits/test/'
TRAIN_NLP_PATH = INPUT_PATH + 'TrainCommits/'
TEST_NLP_PATH = INPUT_PATH + 'TestCommits/'

stopwordList = stopwords.words('english') + list(string.punctuation) + ['_', '', ',']   # stopword 리스트로 만들기

regex_str = [r'<[^>]+',
             r'http[s]?://(?:[a-z]|[0-9]|[$-_@.&amp;+]|[!*\(\),]|(?:%[0-9a-f][0-9a-f]))+',
             r'(?:(?:\d+,?)+(?:\.?\d+)?)',
             r"(?:[a-z][a-z'\-_]+[a-z])",
             r'(?:[\w_]+)',
             r'(?:\S)']

tokens_re = re.compile(r'(' + '|'.join(regex_str) + ')', re.VERBOSE | re.IGNORECASE)

def splitWords(line):    
    return re.findall('[A-Z]*[a-z]+', line)                

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
                
                tokenizedLine = list()
                for line in open(path + '/' + filename, 'r'):                                        
                    tokenizedLine.extend([term.lower().translate(None, '0123456789') for term in tokens_re.findall(line) if term not in stopwordList])
                                
                if len(tokenizedLine) != 0:
                    
                    total_program_doc_num += 1
                    
                    OUTPUT_FILE = open(OUTPUT_PATH + '/' + filename, 'w')
                    OUTPUT_FILE.write(' '.join(tokenizedLine))
                    MERGE_FILE.write(' '.join(tokenizedLine) + '\n')
                    TRAIN_ALL_FILE.write(' '.join(tokenizedLine) + '\n')                    
                    OUTPUT_FILE.close()
                    
                    count_all.update(tokenizedLine)                             # count terms
                    
                    for i in range(len(tokenizedLine) - 1):
                        for j in range(i+1, len(tokenizedLine)):
                            w1, w2 = sorted([tokenizedLine[i].lower(), tokenizedLine[j].lower()])
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
                for line in open(path + '/' + filename, 'r'):                                        
                    tokenizedLine.extend([term.lower().translate(None, '0123456789') for term in tokens_re.findall(line) if term not in stopwordList])
                    
                    if len(tokenizedLine) != 0:                        
                        OUTPUT_FILE = open(OUTPUT_PATH + '/' + filename, 'w')
                        OUTPUT_FILE.write(' '.join(tokenizedLine))
                        OUTPUT_FILE.close()    
    
if __name__ == "__main__":
    
    PROJECT_LIST = ['kotlin','gradle','orientdb','PDE','Actor','hadoop','Graylog','cassandra','CoreNLP','netty','druid','alluxio']
    
    preprocess_train(PROJECT_LIST)
    preprocess_test(PROJECT_LIST)
    
    