# -*- encoding:utf-8-*-
import os, math, numpy
from pymongo import MongoClient

CUR_PATH = os.getcwd()
PREPROCESS_PATH = CUR_PATH + '/TermFrequency/'
INPUT_PATH = CUR_PATH + '/parsedData/'

client = MongoClient('localhost', 27017)
db = client.commit_dictionary    
#db.authenticate('jungbini','esel10582')

termFreqCollection = db.TermFrequency                           # Term Frequency 저장 db collection
cooccurFreqCollection = db.CoOccurenceFrequency                  # Co-occurence Frequency 저장 db collection

def calcPMI(keyword1, keyword2):
    
    t1Freq = -1
    t2Freq = -1
    
    t1Result = termFreqCollection.find_one({"term": keyword1})
    t2Result = termFreqCollection.find_one({"term": keyword2})
    
    if not t1Result:        
        return 0
    if not t2Result:
        return 0
    
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
    PMI = math.log(         (numpy.float64(cooccurFreq)/totalDocNum) / 
                    ( (numpy.float64(t1Freq)/totalDocNum) * (numpy.float64(t2Freq)/totalDocNum)) )
    
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
    
    print 'inserting term frequency data to TermFrequency collection from mongoDB...'
    termFreqCollection.insert_many([{"term": line.split('|')[0], "freq": int(line.split('|')[1])} for line in open(PREPROCESS_PATH + 'TermFreq.txt', 'r') if line.strip()])
             
    print 'inserting co-occurence frequency data to CoOccurenceFrequency collection from mongoDB...'
    cooccurFreqCollection.insert_many([{"term1": line.split('|')[0], "term2": line.split('|')[1], "freq": int(line.split('|')[2])} for line in open(PREPROCESS_PATH + 'CoOccurenceFreq.txt', 'r')])    

# if __name__ == "__main__":        
#     saveMongoDB()
#     calcPMI("error", "java")