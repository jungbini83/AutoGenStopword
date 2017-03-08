# -*- encoding:utf-8-*-
import os, math, numpy
from pymongo import MongoClient
from pymongo import IndexModel, ASCENDING

CUR_PATH = os.getcwd()
PREPROCESS_PATH = CUR_PATH + '/TermFrequency/'
INPUT_PATH = CUR_PATH + '/parsedData/'

client = MongoClient('mongodb://localhost', 27017)
# client = MongoClient('mongodb://192.168.219.103', 27017)
# client = MongoClient('mongodb://163.152.161.97', 27017)
db = client.commit_dictionary    

termFreqCollection = db.TermFrequency                           # Term Frequency 저장 db collection
cooccurFreqCollection = db.CoOccurenceFrequency                  # Co-occurence Frequency 저장 db collection

def calcPMI(keyword1, keyword2):
    
    t1Freq = -1
    t2Freq = -1
    
    queryt1 = termFreqCollection.find_one({"term": keyword1})
    queryt2 = termFreqCollection.find_one({"term": keyword2})
    
    if not queryt1:        return 0
    if not queryt2:        return 0
    
    t1Freq = int(queryt1["freq"])    
    t2Freq = int(queryt2["freq"])
    
    cooccurFreq = -1
    
    cooccurResult = cooccurFreqCollection.find_one({"term1": keyword1, "term2": keyword2})
    
    if cooccurResult:
        cooccurFreq = cooccurResult["freq"]
    else:
        cooccurResult = cooccurFreqCollection.find_one({"term1": keyword2, "term2": keyword1})
    
    if cooccurResult:
        cooccurFreq = cooccurResult["freq"]
    else:
        return 0
                
    totalDocNum = int(open(PREPROCESS_PATH + 'TotalDocNum.txt', 'r').read())
    
    # PMI 계산하기
    denominator = numpy.float64(cooccurFreq)/totalDocNum
    numerator   = (numpy.float64(t1Freq)/totalDocNum) * (numpy.float64(t2Freq)/totalDocNum)
    PMI = math.log(denominator / numerator)
    
    return PMI

def calcPMIfromFile(keyword1, keyword2):

    t1Freq = -1
    t2Freq = -1
    for line in open(PREPROCESS_PATH + 'TermFreq.txt', 'r'):
        
        tokenizedLine = line.split('|')
        
        if keyword1 == tokenizedLine[0]:        t1Freq = int(line.split('|')[1])
        if keyword2 == tokenizedLine[0]:        t2Freq = int(line.split('|')[1])
        
        if t1Freq != -1 and t2Freq != -1:       break;
        
    if t1Freq == -1 or t2Freq == -1:                    # 둘 중에 하나라도 없으면 동시에 나타날 수도 없음
        return 0
    
    cooccurFreq = -1
    for line in open(PREPROCESS_PATH + 'CoOccurenceFreq.txt', 'r'):
        
        tokenizedLine = line.split('|')
        
        if keyword1 == tokenizedLine[0]:
            if keyword2 == tokenizedLine[1]:                
                cooccurFreq = int(tokenizedLine[2])
                break;
        if keyword1 == tokenizedLine[1]:
            if keyword2 == tokenizedLine[0]:
                cooccurFreq = int(tokenizedLine[2])
                break;
    
    if cooccurFreq == -1:                               # 역시 동시에 나타나지 않으면 분모가 0
        return 0
                
    totalDocNum = int(open(PREPROCESS_PATH + 'TotalDocNum.txt', 'r').read())
    
    # PMI 계산하기
    PMI = math.log(         (numpy.float64(cooccurFreq)/totalDocNum) / 
                    ( (numpy.float64(t1Freq)/totalDocNum) * (numpy.float64(t2Freq)/totalDocNum)) )
    
    return PMI

def saveMongoDB():
    
    # 일단 그전 DB는 모두 지우고 시작
    termFreqCollection.drop()
    cooccurFreqCollection.drop()    
    
    print 'inserting term frequency data to TermFrequency collection from mongoDB...'
    termFreqCollection.insert_many([{"term": line.split('|')[0], "freq": int(line.split('|')[1])} for line in open(PREPROCESS_PATH + 'TermFreq.txt', 'r') if line.strip()])
    
    # 인덱스 만들기
    index = IndexModel([("term", ASCENDING)])
    termFreqCollection.create_indexes([index])
                 
    print 'inserting co-occurence frequency data to CoOccurenceFrequency collection from mongoDB...'
    cooccurFreqCollection.insert_many([{"term1": line.split('|')[0], "term2": line.split('|')[1], "freq": int(line.split('|')[2])} for line in open(PREPROCESS_PATH + 'CoOccurenceFreq.txt', 'r')])
    
    # 인덱스 만들기
    index1 = IndexModel([("term1", ASCENDING)])
    index2 = IndexModel([("term2", ASCENDING)])
    cooccurFreqCollection.create_indexes([index1, index2])
    
def calcPMIMetrix(wordList1, wordList2):
    
    row, col = 20, 20
    PMIMatrix = [[0 for x in range(col)] for y in range(row)]
        
    PMIList = list()
    totalSumOfPMI = 0
    for mRow in range(0, len(wordList1)):
            
        sumOfPMI = 0
        for mCol in range(0, len(wordList2)):
                
            pmiValue = calcPMI(wordList1[mRow],wordList2[mCol])
            sumOfPMI += pmiValue
            
            PMIMatrix[mRow][mCol] = pmiValue
            PMIMatrix[mCol][mRow] = pmiValue
        
        totalSumOfPMI += sumOfPMI
        PMIList.append(str(sumOfPMI))
    
    return totalSumOfPMI
    
if __name__ == "__main__":        
    saveMongoDB()
    print calcPMI("svn", "ffa") 