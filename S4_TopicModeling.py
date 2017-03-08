# -*- encoding:utf-8-*-
import os, math, random, shutil
import S3_CalcPMI

CUR_PATH = os.getcwd()
PREPROCESS_PATH = CUR_PATH + '/TermFrequency/'
INPUT_PATH = CUR_PATH + '/parsedData/'
TRAIN_PATH = INPUT_PATH + '/Commits/'
TRAIN_NLP_PATH = INPUT_PATH + '/TrainCommits/'
TEST_NLP_PATH = INPUT_PATH + '/TestCommits/'
TM_OUTPUT_PATH = CUR_PATH + '/TMOutput/'

if not os.path.exists(TM_OUTPUT_PATH):
    os.makedirs(TM_OUTPUT_PATH)

def randomSelTestfile():
    
    os.chdir(CUR_PATH + '/mallet/bin/')  
    
    for tryIdx in range(1, SAMPLE_NUM+1):                                               # 10踰� sample �뙆�씪�쓣 �옖�뜡�쑝濡� 異붿텧
        
        SAMPLE_DOC_PATH = CUR_PATH + '/sampleDoc/Sample' + str(tryIdx)
        
        if os.path.exists(SAMPLE_DOC_PATH):
            shutil.rmtree(SAMPLE_DOC_PATH)                                              # 癒쇱� 湲곗〈 �깦�뵆�뙆�씪 吏��슦湲�
        if not os.path.exists(SAMPLE_DOC_PATH):
            os.makedirs(SAMPLE_DOC_PATH)
            
        # Test �뙆�씪 由ъ뒪�듃�뿉�꽌 �뙆�씪�쓣 �옖�뜡�쑝濡� 異붿텧
        testFileList = list()
        for path, dir, files in os.walk(TRAIN_NLP_PATH):
            testFileList.extend([path + '/' + fileName for fileName in files])
        
        sampleDoc = random.sample(testFileList, 2000)                               # �쟾泥� 臾몄꽌�쓽 20%瑜� �꽑�깮
            
        fileIdx = 1
        for filePath in sampleDoc:
            print '#' + str(tryIdx) + ' Sample [' + str(fileIdx) + '/2000] copying filename is \'' + filePath + '\'.'
            shutil.copy(filePath, SAMPLE_DOC_PATH)
            fileIdx+=1
            
    os.chdir('..')

def makeTestFileBoW():
    
    os.chdir(CUR_PATH + '/mallet/bin/')

    for tryIdx in range(1, SAMPLE_NUM+1):
        
        SAMPLE_DOC_PATH = CUR_PATH + '/sampleDoc/Sample' + str(tryIdx)
                
        print '�봽濡쒓렇�옩 蹂� Test�슜 Basket of Words 留뚮뱾湲�'        
        cmd_result = os.system('mallet import-dir --input ' + SAMPLE_DOC_PATH + ' --keep-sequence --output ' + TM_OUTPUT_PATH + '/test_corpus(' + str(tryIdx) + ').mallet')
        if not cmd_result == 0:
            print 'Error..\n'
            
    os.chdir('..')

def makeTrainFileBoW(type, evalNum):
    
    os.chdir(CUR_PATH + '/mallet/bin/')
    
    # Train�슜 corpus 留뚮뱾湲�
    print 'Train�슜 Basket of Words 留뚮뱾湲�'
    
    if type == 'Standard':
        cmd_result = os.system('mallet import-file --input ' + TRAIN_NLP_PATH + 'commits(train).txt --keep-sequence --stoplist-file ../stoplists/fox_stopwords.txt --output ' + TM_OUTPUT_PATH + '/train_corpus.mallet')
    elif type == 'Poisson':
        cmd_result = os.system('mallet import-file --input ' + TRAIN_NLP_PATH + 'commits(train).txt --keep-sequence --stoplist-file ../stoplists/poisson_stopwords.txt --output ' + TM_OUTPUT_PATH + '/train_corpus.mallet')
    elif type == 'RAKE':
        cmd_result = os.system('mallet import-file --input ' + TRAIN_NLP_PATH + 'commits(train).txt --keep-sequence --stoplist-file ../stoplists/rake_stopwords.txt --output ' + TM_OUTPUT_PATH + '/train_corpus.mallet')
    elif type == 'AutoGen':
        cmd_result = os.system('mallet import-file --input ' + TRAIN_NLP_PATH + 'commits(train).txt --keep-sequence --stoplist-file ../stoplists/TopClass_extra(' + str(evalNum) + ').txt --output ' + TM_OUTPUT_PATH + '/train_corpus.mallet')
#     cmd_result = os.system('mallet import-file --input ' + TRAIN_NLP_PATH + 'commits(train).txt --remove-stopwords --stoplist-file ../stoplists/TopClass_extra.txt --keep-sequence --output ' + TM_OUTPUT_PATH + '/train_corpus.mallet')
    if not cmd_result == 0:
        print 'Error..\n'
            
    os.chdir('..')
    
# Topic Modeling �룎由ш린
def runTM(tryIdx):
    
    os.chdir(CUR_PATH + '/mallet/bin')  
    
    # 1. Train File 紐⑤뜽留�
    cmd_result = os.system('mallet train-topics --input ' + TM_OUTPUT_PATH + 'train_corpus.mallet --num-topics ' + str(TOPIC_NUMBER) +
                             ' --evaluator-filename ' + TM_OUTPUT_PATH + 'evaluator' 
                             ' --output-topic-keys ' + TM_OUTPUT_PATH + 'AssociatedWords(' + str(tryIdx) + '-' + str(TOPIC_NUMBER) + ').csv' + 
                             ' --output-doc-topics ' + TM_OUTPUT_PATH + 'TopicContribution(' + str(TOPIC_NUMBER) + ').csv' +
                             ' --num-iterations 300 --show-topics-interval 1000 ' +
                             ' --num-threads 16')
      
    if not cmd_result == 0:
        print 'Train topic model �뿉�윭 諛쒖깮\n'
        exit()
    
    # 2. �깦�뵆 Test File 紐⑤뜽留�
    for tryIdx in range(1, SAMPLE_NUM+1):
                
        cmd_result = os.system('mallet evaluate-topics --evaluator ' + TM_OUTPUT_PATH + 'evaluator' 
                               ' --input ' + TM_OUTPUT_PATH + 'test_corpus(' + str(tryIdx) + ').mallet' + 
                               ' --output-doc-probs ' + TM_OUTPUT_PATH + 'docprobs(' + str(tryIdx) + ').txt')
        
        if not cmd_result == 0:
            print 'Test topic model �뿉�윭 諛쒖깮\n'
            exit()
                   
        # Document length 援ы븯湲�
        cmd_result = os.system('mallet run cc.mallet.util.DocumentLengths' +
                               ' --input ' + TM_OUTPUT_PATH + 'test_corpus(' + str(tryIdx) + ').mallet' +
                               ' > ' + TM_OUTPUT_PATH + 'doclengths(' + str(tryIdx) +').txt')
        
    os.chdir('../..')
    
def calcPerplexity(evalNum, tryNum): 
    
    OUTPUT_FILE = open(TM_OUTPUT_PATH + 'perplexity(' + str(evalNum) + '-' + str(tryNum) + ').txt', 'w')
        
    # �깦�뵆 test file�쓽 Perplexity 怨꾩궛
    sumOfPerplexity = 0
    for tryIdx in range(1, SAMPLE_NUM+1):
    
        logLikelihood   = [float(ll) for ll in open(TM_OUTPUT_PATH + 'docprobs(' + str(tryIdx) + ').txt')]
        docLength       = [int(length) for length in open(TM_OUTPUT_PATH + 'doclengths(' + str(tryIdx) + ').txt')] 
        
        sumOfLL     = sum(logLikelihood)
        sumOfDocLen = sum(docLength)
        perplexity  = math.exp(-sumOfLL / sumOfDocLen)
        sumOfPerplexity += perplexity                                       # �룊洹좎쓣 �궡湲� �쐞�빐 �빀�궛
        
        OUTPUT_FILE.write(str(perplexity) + '\n')
        
    OUTPUT_FILE.write(str(sumOfPerplexity/SAMPLE_NUM) + '\n')
    
    return sumOfPerplexity/SAMPLE_NUM
            
def calcTopicCoherence(tryIdx):
   
    row, col = TOPIC_NUMBER, TOPIC_NUMBER
    PMIMatrix = [[0 for x in range(col)] for y in range(row)]
        
    topicNum = 0
    stopwordList = list()
    for line in open(TM_OUTPUT_PATH + '/AssociatedWords(' + str(tryIdx) + '-'  + str(TOPIC_NUMBER) + ').csv'):            
 
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
            if minSumPMI > sum(PMIMatrix[mRow]):                    # PMI�쓽 �빀�씠 �옉�� word瑜� �꽑�깮�빐�꽌 吏��슫�떎.(�쟾泥� �떒�뼱�뱾怨� 愿��젴�꽦�씠 媛��옣 �옉�떎)
                minIdx = mRow
                minSumPMI = sum(PMIMatrix[mRow])
        
        stopwordList.append(topicWords[minIdx])
        
    return stopwordList

def calcTopicCoherece2(stopwordList, tryIdx):
    
    minCoherence = 1000
    removeStopword = ''
    for line in open(TM_OUTPUT_PATH + '/AssociatedWords(' + str(tryIdx) + '-' + str(TOPIC_NUMBER) + ').csv'):
        
        tokenedLine = line.split()[2:12]
    
        for sword in stopwordList:
            pmiValueList = [S3_CalcPMI.calcPMI(sword, targetword) for targetword in tokenedLine]
            minIndex = pmiValueList.index(min(pmiValueList))
            
            if minCoherence > pmiValueList[minIndex]:
                minCoherence = pmiValueList[minIndex]
                removeStopword = tokenedLine[minIndex]
                
    print 'Final stopword is "' + removeStopword + '".'
    return removeStopword

if __name__ == "__main__":
    
    TOPIC_NUMBER = 10
    SAMPLE_NUM  = 30 
    PROJECT_LIST = ['kotlin','gradle','orientdb','PDE','Actor','hadoop','Graylog','cassandra','CoreNLP','netty','druid','alluxio']
    
    for evalNum in range(1, 2):
            
        PerplexityResult = list()
        PERPLEXITY_OUTPUT = open(TM_OUTPUT_PATH + '/AvgPerplexity(' + str(evalNum) + ').txt', 'w')
        
        STOPWORD_FILE = open(CUR_PATH + '/mallet/stoplists/TopClass_extra(' + str(evalNum) + ').txt', 'w') 
             
#         randomSelTestfile()
        makeTestFileBoW()
         
        makeTrainFileBoW('Standard', evalNum)
        runTM('Standard')
        PerplexityResult.append(str(calcPerplexity(evalNum, 'Foxlist')))
        
        makeTrainFileBoW('Poisson', evalNum)
        runTM('Poisson')
        PerplexityResult.append(str(calcPerplexity(evalNum, 'Poisson')))
         
        makeTrainFileBoW('RAKE', evalNum)
        runTM('RAKE')
        PerplexityResult.append(str(calcPerplexity(evalNum, 'RAKE')))
        
        for tryIdx in range(1,422):
            
            makeTrainFileBoW('AutoGen', evalNum)
            runTM(tryIdx)
            PerplexityResult.append(str(calcPerplexity(evalNum, tryIdx)))                  # �룊洹� perplexity 諛쏄린
             
            candidateStopwords = calcTopicCoherence(tryIdx)        
            existingStopword = [line.strip() for line in open(CUR_PATH + '/mallet/stoplists/TopClass_extra(' + str(evalNum) + ').txt', 'r')]        
            existingStopword.append(calcTopicCoherece2(candidateStopwords, tryIdx))    # �넗�뵿蹂� stopword�뿉�꽌 �떎�떆 1媛� 戮묒븘�꽌 異붽�
                
            STOPWORD_FILE = open(CUR_PATH + '/mallet/stoplists/TopClass_extra(' + str(evalNum) + ').txt', 'w')
            STOPWORD_FILE.write('\n'.join(existingStopword))            # Extra stopword �뙆�씪�뿉 �벐湲�
            STOPWORD_FILE.flush()
            print existingStopword      
#             
        PERPLEXITY_OUTPUT.write('\n'.join(PerplexityResult))       