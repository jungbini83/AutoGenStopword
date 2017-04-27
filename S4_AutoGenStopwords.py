# -*- encoding:utf-8-*-
import os, math, random, shutil
import S3_CalcPMI
from collections import defaultdict

CUR_PATH = os.getcwd()
PREPROCESS_PATH = CUR_PATH + '/TermFrequency/'
INPUT_PATH = CUR_PATH + '/parsedData/'
TRAIN_PATH = INPUT_PATH + '/Commits/'
TRAIN_NLP_PATH = INPUT_PATH + '/TrainCommits/'
TEST_NLP_PATH = INPUT_PATH + '/TestCommits/'
TM_OUTPUT_PATH = CUR_PATH + '/TMOutput/'
EXTERNAL_DOC_PATH = CUR_PATH + '/parsedData/TestCommits'    # External Test Source file Path

# Projects for experiment
PROJECT_LIST = ['kotlin','gradle','orientdb','PDE','Actor','hadoop','Graylog','cassandra','CoreNLP','netty','druid','alluxio']
    
TOPIC_NUMBER    = 10                # Number of Topics   
STOPWORD_NUM    = 422               # Number of Stop Words to make
SAMPLE_NUM      = 30                # Number of Samples of internal test source files


# Selecting Source Files Randomly from Each Project
def randomSelTestfile(SAMPLE_NUM):
    
    os.chdir(CUR_PATH + '/mallet/bin/')    
    
    SAMPLE_DOC_PATH = CUR_PATH + '/sampleDoc/'                            # Sample directory path
    
    # If there are existing sample source files, delete all files and dirs
    if os.path.exists(SAMPLE_DOC_PATH):                               
        shutil.rmtree(SAMPLE_DOC_PATH)     
    
    # Repeat sampling for SAMPLE_NUM
    for sampleIdx in range(1, SAMPLE_NUM+1):                                               
        
        FINAL_SAMPLE_PATH = SAMPLE_DOC_PATH + 'Sample' + str(sampleIdx)
        
        # Make sample directory                                              
        os.makedirs(FINAL_SAMPLE_PATH)                                      
        
        # Collect all test source files in Train Path (Internal)
        print 'Collecting test source files for Sample#' + str(sampleIdx) + '...'
        testFileList = list()                                                           
        for path, dir, files in os.walk(TRAIN_NLP_PATH):
            testFileList.extend([path + '/' + fileName for fileName in files])
        
        # Sampling 2000 files from testFileList for each sample
        sampleDoc = random.sample(testFileList, 2000)                               
        
        # Copy selected source files to sample directory
        print 'Copy source files of Sample#' + str(sampleIdx) + ' to sample directory...'
        for filePath in sampleDoc:            
            shutil.copy(filePath, FINAL_SAMPLE_PATH)        
            
    os.chdir('..')

def makeInternalFileBoW(SAMPLE_NUM):
    
    os.chdir(CUR_PATH + '/mallet/bin/')
    
    SAMPLE_DOC_PATH = CUR_PATH + '/sampleDoc/Sample'                            # Sample directory path  

    # Repeat making BoW curpus files for SAMPLE_NUM
    for tryIdx in range(1, SAMPLE_NUM+1):
                
        print 'Making BoW of sample#' + str(SAMPLE_NUM) + '\'s documents...'       
        
        cmd_result = os.system('mallet import-dir --input ' + SAMPLE_DOC_PATH + str(tryIdx) + ' --keep-sequence --output ' + TM_OUTPUT_PATH + '/test_corpus_sample#' + str(tryIdx) + '.mallet')
        
        if not cmd_result == 0:
            print 'Occur error in makeInternalFileBoW function.\n'
            
    os.chdir('..')
    
def makeExternalFileBoW():
    
    os.chdir(CUR_PATH + '/mallet/bin/')
    
    EXTERNAL_DOC_PATH = CUR_PATH + '/parsedData/TestCommits'
    
    print 'making External data set to BoW...'
    cmd_result = os.system('mallet import-dir --input ' + EXTERNAL_DOC_PATH + ' --keep-sequence --output ' + TM_OUTPUT_PATH + '/external_corpus.mallet')
    if not cmd_result == 0:
        print 'Error..\n'
            
    os.chdir('..')

def makeTrainFileBoW(APPROACH, evalNum, typeOfData):
    
    os.chdir(CUR_PATH + '/mallet/bin/')
    
    INIT_STOPWORD_FILE = '../stoplists/' + APPROACH + '_Eval#' + str(evalNum) + '_' + typeOfData + '.txt' 
    
    if not os.path.isfile(INIT_STOPWORD_FILE):
        open(INIT_STOPWORD_FILE, 'w')        
    
    # Making BoW of train source files
    print 'Making BoW of train source files using ' + APPROACH + '\'s stop word list...'     
    COMMON_CMD = 'mallet import-file --input ' + TRAIN_NLP_PATH + 'commits(train).txt --keep-sequence --output ' + TM_OUTPUT_PATH + '/train_corpus.mallet  --stoplist-file ' + INIT_STOPWORD_FILE    
    cmd_result = os.system(COMMON_CMD)
        
    if not cmd_result == 0:
        print 'Error..\n'
            
    os.chdir('..')

def makeTrainFileBoW4Evaluation(APPROACH, typeOfData):
    
    os.chdir(CUR_PATH + '/mallet/bin/')
    
    if APPROACH == 'AutoGen':
        STOPWORD_FILE = '../stoplists/' + APPROACH + '_' + typeOfData + '.txt'
    elif APPROACH == 'FOX':
        STOPWORD_FILE = '../stoplists/fox_stopwords.txt'
    elif APPROACH == 'POISSON':
        STOPWORD_FILE = '../stoplists/poisson_stopwords.txt'
    elif APPROACH == 'rake':
        STOPWORD_FILE = '../stoplists/rake_stopwords.txt'
    
    # Making BoW of train source files
    print 'Making BoW of train source files using ' + APPROACH + '\'s stop word list...'     
    COMMON_CMD = 'mallet import-file --input ' + TRAIN_NLP_PATH + 'commits(train).txt --keep-sequence --output ' + TM_OUTPUT_PATH + '/train_corpus.mallet  --stoplist-file ' + STOPWORD_FILE    
    cmd_result = os.system(COMMON_CMD)
        
    if not cmd_result == 0:
        print 'Error..\n'
            
    os.chdir('..')


def makeTrainTM(NumOfStopWord):
    
    os.chdir(CUR_PATH + '/mallet/bin')  
    
    # Making Train File to Topic Model
    cmd_result = os.system('mallet train-topics --input ' + TM_OUTPUT_PATH + 'train_corpus.mallet --num-topics ' + str(TOPIC_NUMBER) + ' --evaluator-filename ' + TM_OUTPUT_PATH + 'evaluator' +
                           ' --output-topic-keys ' + TM_OUTPUT_PATH + 'AssociatedWords(' + str(NumOfStopWord) + '-' + str(TOPIC_NUMBER) + ').csv' + 
                             ' --output-doc-topics ' + TM_OUTPUT_PATH + 'TopicContribution(' + str(TOPIC_NUMBER) + ').csv --num-iterations 300 --show-topics-interval 1000 --num-threads 16')
      
    if not cmd_result == 0:
        print 'Topic modeling of Train source files...\n'
        exit()

def runTM(NumOfStopWord, TypeOfData):
    
    os.chdir(CUR_PATH + '/mallet/bin')  
    
    # 1. Making Train corpus to Topic Model
    makeTrainTM(NumOfStopWord)    
    
    # 2. Making Internal data set corpus to Topic Model
    if TypeOfData == 'Internal':
        
        for sampleIdx in range(1, SAMPLE_NUM+1):
                    
            cmd_result = os.system('mallet evaluate-topics --evaluator ' + TM_OUTPUT_PATH + 'evaluator --input ' + TM_OUTPUT_PATH + 'test_corpus_sample#' + 
                                   str(sampleIdx) + '.mallet --output-doc-probs ' + TM_OUTPUT_PATH + 'internal_docprobs(' + str(sampleIdx) + ').txt')
            
            if not cmd_result == 0:
                print 'Internal test topic model error...'                
                       
            # 3. Document length calculation...
            cmd_result = os.system('mallet run cc.mallet.util.DocumentLengths --input ' + TM_OUTPUT_PATH + 'test_corpus_sample#' + 
                                   str(sampleIdx) + '.mallet > ' + TM_OUTPUT_PATH + 'internal_doclengths(' + str(sampleIdx) +').txt')
    else:
        cmd_result = os.system('mallet evaluate-topics --evaluator ' + TM_OUTPUT_PATH + 'evaluator --input ' + TM_OUTPUT_PATH + 'external_corpus.mallet' + 
                               ' --output-doc-probs ' + TM_OUTPUT_PATH + 'external_docprobs.txt')
        
        if not cmd_result == 0:
            print 'External test topic model error...'
            
        # 3. Document length calculation...
        cmd_result = os.system('mallet run cc.mallet.util.DocumentLengths --input ' + TM_OUTPUT_PATH + 'external_corpus.mallet' +
                               ' > ' + TM_OUTPUT_PATH + 'external_doclengths.txt')
        
    os.chdir('../..')
    
# Measuring internal test file perplexity
def calcPerplexity4Internal(evalNum, tryNum): 
    
    OUTPUT_FILE = open(TM_OUTPUT_PATH + 'internal_perplexity(' + str(evalNum) + '-' + str(tryNum) + ').txt', 'w')
    
    sumOfPerplexity = 0
    for sampleIdx in range(1, SAMPLE_NUM+1):
    
        logLikelihood   = [float(ll) for ll in open(TM_OUTPUT_PATH + 'internal_docprobs(' + str(sampleIdx) + ').txt')]
        docLength       = [int(length) for length in open(TM_OUTPUT_PATH + 'internal_doclengths(' + str(sampleIdx) + ').txt')] 
        
        sumOfLL     = sum(logLikelihood)
        sumOfDocLen = sum(docLength)
        perplexity  = math.exp(-sumOfLL / sumOfDocLen)
        sumOfPerplexity += perplexity                                       # Accumulating perplexity of each sample
        
        OUTPUT_FILE.write(str(perplexity) + '\n')
        
    OUTPUT_FILE.write(str(sumOfPerplexity/SAMPLE_NUM) + '\n')
    
    return sumOfPerplexity/SAMPLE_NUM
            
# Measuring external test file perplexity
def calcPerplexity4External(evalNum): 
    
    OUTPUT_FILE = open(TM_OUTPUT_PATH + 'external_perplexity(' + str(evalNum) + ').txt', 'w')
     
    logLikelihood   = [float(ll) for ll in open(TM_OUTPUT_PATH + 'external_docprobs.txt')]
    docLength       = [int(length) for length in open(TM_OUTPUT_PATH + 'external_doclengths.txt')] 
    
    sumOfLL     = sum(logLikelihood)
    sumOfDocLen = sum(docLength)
    perplexity  = math.exp(-sumOfLL / sumOfDocLen)
        
    OUTPUT_FILE.write(str(perplexity) + '\n')
    OUTPUT_FILE.flush()
    
    return perplexity            

def calcWordPMI(NumOfStopword):
   
    row, col = TOPIC_NUMBER, TOPIC_NUMBER
    PMIMatrix = [[0 for x in range(col)] for y in range(row)]
        
    topicNum = 0
    stopwordList = list()
    for line in open(TM_OUTPUT_PATH + '/AssociatedWords(' + str(NumOfStopword) + '-'  + str(TOPIC_NUMBER) + ').csv'):            
 
        topicWords = line.split()[2:12]
 
        for mRow in range(0, len(topicWords)-1):
            
            for mCol in range(mRow+1, len(topicWords)):

                pmiValue = S3_CalcPMI.calcPMI(topicWords[mRow],topicWords[mCol])
                
                print "[Topic" + str(topicNum) + "] PMI value between " + topicWords[mRow] + " and " + topicWords[mCol] + ": "  + str(pmiValue)
                 
                PMIMatrix[mRow][mCol] = pmiValue
                PMIMatrix[mCol][mRow] = pmiValue
                            
        topicNum += 1
        
        for mRow in range(0,len(PMIMatrix)):
            print PMIMatrix[mRow]
            
        minIdx = -1
        minSumPMI = 1000
        for mRow in range(0,len(PMIMatrix)):
            if minSumPMI > sum(PMIMatrix[mRow]):                    # Find stopword alternatives with minimum PMI value at each row
                minIdx = mRow
                minSumPMI = sum(PMIMatrix[mRow])
        
        stopwordList.append(topicWords[minIdx])
        
    return stopwordList

def calcTopicPMI(stopwordList, NumOfStopword):
    
    minCoherence = 1000
    removeStopword = ''
    for line in open(TM_OUTPUT_PATH + '/AssociatedWords(' + str(NumOfStopword) + '-' + str(TOPIC_NUMBER) + ').csv'):
        
        tokenedLine = line.split()[2:12]
    
        for sword in stopwordList:
            pmiValueList = [S3_CalcPMI.calcPMI(sword, targetword) for targetword in tokenedLine]
            minIndex = pmiValueList.index(min(pmiValueList))
            
            if minCoherence > pmiValueList[minIndex]:
                minCoherence = pmiValueList[minIndex]
                removeStopword = tokenedLine[minIndex]
                
    print 'Final stopword is "' + removeStopword + '".'
    return removeStopword

def AutoGenStopwords(TypeOfData, STOPWORD_NUM):
    
    EVALUATION_NUM = 1
    
    if TypeOfData == 'Internal':
            
        randomSelTestfile(SAMPLE_NUM)           # 1. Making Internal File BoW
        makeInternalFileBoW(SAMPLE_NUM)
    
    elif TypeOfData == 'External':
                
        makeExternalFileBoW()                   # 1. Making External File BoW    
        
    # 2. Generating stop words automatically    
    for evalNum in range(0, EVALUATION_NUM):
    
        PerplexityResult = list()    
        for NumOfStopword in range(1,STOPWORD_NUM+1):
            
            # 2-1. Training train source files using new stop words and Running topic modeling
            makeTrainFileBoW('AutoGen', evalNum, TypeOfData)        
            runTM(NumOfStopword, TypeOfData)
            
            # 2-2. Measure perplexity of new topic model and add it to PerplexityResult list
            if TypeOfData == 'Internal':
                perplexity = calcPerplexity4Internal(evalNum, NumOfStopword)
            elif TypeOfData == 'External':
                perplexity = calcPerplexity4External(evalNum)
            
            PerplexityResult.append(str(perplexity))
             
            # 2-3. Calculate Word and Topic PMI (Extracting K stop word candidates -> Choosing final a single stop word among them)
            candidateStopwords = calcWordPMI(NumOfStopword)
            finalStopword = calcTopicPMI(candidateStopwords, NumOfStopword)
            print 'Adding \'' + finalStopword + '\' to our stop word list...'
    
            # 2-4. Add final stop word to our stop word list            
            with open(CUR_PATH + '/mallet/stoplists/AutoGen_Eval#' + str(evalNum) + '_' + TypeOfData +  '.txt', 'a') as STOPWORD_FILE:
                STOPWORD_FILE.write(finalStopword + '\n')   
            
        # Write Average of Perplexity
        with open(TM_OUTPUT_PATH + '/AVG_Perplexity-' + str(evalNum) + '.txt', 'w') as PERPLEXITY_OUTPUT:
           PERPLEXITY_OUTPUT.write('\n'.join(PerplexityResult))   
     
# If each stop word lists are made completely, this function can evaluate each approach
def TM4Evaluation(dataType):
    
    if dataType == 'Internal':
        randomSelTestfile()
        makeInternalFileBoW()
    else:
        makeExternalFileBoW()
                
    for approach in ['AutoGen']:

        PERPLEXITY_OUTPUT = open(TM_OUTPUT_PATH + '/Perplexity(' + approach + ').txt', 'w')
        makeTrainFileBoW4Evaluation(approach, TypeOfData)
        
        runTM(NumOfStopword, TypeOfData)
        
        if dataType == 'Internal':
            perplexity = calcPerplexity4Internal(evalNum, NumOfStopword)
            PERPLEXITY_OUTPUT.write(str(perplexity))
        else:   
            for tryIdx in range(1,31):
                perplexity = calcPerplexity4External(evalNum)
                PERPLEXITY_OUTPUT.write(str(perplexity) + '\n')
                PERPLEXITY_OUTPUT.flush()        
            
if __name__ == "__main__":
    
    AutoGenStopwords('Internal', STOPWORD_NUM)
    AutoGenStopwords('External', STOPWORD_NUM)

    TM4Evaluation('Internal')
    TM4Evaluation('External')

