# -*- encoding:utf-8-*-
import os, math, random, shutil
import S3_CalcPMI
from collections import defaultdict

TOPIC_NUMBER = 10
SAMPLE_NUM  = 1 
PROJECT_LIST = ['kotlin','gradle','orientdb','PDE','Actor','hadoop','Graylog','cassandra','CoreNLP','netty','druid','alluxio']

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
    
    for tryIdx in range(1, SAMPLE_NUM+1):                                               # 10甕곤옙 sample 占쎈솁占쎌뵬占쎌뱽 占쎌삏占쎈쑁占쎌몵嚥∽옙 �빊遺욱뀱
        
        SAMPLE_DOC_PATH = CUR_PATH + '/sampleDoc/Sample' + str(tryIdx)
        
        if os.path.exists(SAMPLE_DOC_PATH):
            shutil.rmtree(SAMPLE_DOC_PATH)                                              # �솒�눘占� 疫꿸퀣�� 占쎄묘占쎈탣占쎈솁占쎌뵬 筌욑옙占쎌뒭疫뀐옙
        if not os.path.exists(SAMPLE_DOC_PATH):
            os.makedirs(SAMPLE_DOC_PATH)
            
        # Test 占쎈솁占쎌뵬 �뵳�딅뮞占쎈뱜占쎈퓠占쎄퐣 占쎈솁占쎌뵬占쎌뱽 占쎌삏占쎈쑁占쎌몵嚥∽옙 �빊遺욱뀱
        testFileList = list()
        for path, dir, files in os.walk(TRAIN_NLP_PATH):
            testFileList.extend([path + '/' + fileName for fileName in files])
        
        sampleDoc = random.sample(testFileList, 2000)                               # 占쎌읈筌ｏ옙 �눧紐꾧퐣占쎌벥 20%�몴占� 占쎄퐨占쎄문
            
        fileIdx = 1
        for filePath in sampleDoc:
            print '#' + str(tryIdx) + ' Sample [' + str(fileIdx) + '/2000] copying filename is \'' + filePath + '\'.'
            shutil.copy(filePath, SAMPLE_DOC_PATH)
            fileIdx+=1
            
    os.chdir('..')

def makeInternalFileBoW():
    
    os.chdir(CUR_PATH + '/mallet/bin/')

    for tryIdx in range(1, SAMPLE_NUM+1):
        
        SAMPLE_DOC_PATH = CUR_PATH + '/sampleDoc/Sample' + str(tryIdx)
                
        print '占쎈늄嚥≪뮄�젃占쎌삪 癰귨옙 Test占쎌뒠 Basket of Words 筌띾슢諭얏묾占�'        
        cmd_result = os.system('mallet import-dir --input ' + SAMPLE_DOC_PATH + ' --keep-sequence --output ' + TM_OUTPUT_PATH + '/test_corpus(' + str(tryIdx) + ').mallet')
        if not cmd_result == 0:
            print 'Error..\n'
            
    os.chdir('..')
    
def makeExternalFileBoW():
    
    os.chdir(CUR_PATH + '/mallet/bin/')
    
    EXTERNAL_DOC_PATH = CUR_PATH + '/parsedData/TestCommits'
    
    print 'making External data set to BoW...'
    cmd_result = os.system('mallet import-dir --input ' + EXTERNAL_DOC_PATH + ' --keep-sequence --output ' + TM_OUTPUT_PATH + '/external_corpus.mallet')
    if not cmd_result == 0:
        print 'Error..\n'
            
    os.chdir('..')

def makeTrainFileBoW(type, evalNum):
    
    os.chdir(CUR_PATH + '/mallet/bin/')
    
    # Train占쎌뒠 corpus 筌띾슢諭얏묾占�
    print 'Train占쎌뒠 Basket of Words 筌띾슢諭얏묾占�'
    
    if type == 'Foxlist':
        cmd_result = os.system('mallet import-file --input ' + TRAIN_NLP_PATH + 'commits(train).txt --keep-sequence --stoplist-file ../stoplists/fox_stopwords.txt --output ' + TM_OUTPUT_PATH + '/train_corpus.mallet')
    elif type == 'Poisson':
        cmd_result = os.system('mallet import-file --input ' + TRAIN_NLP_PATH + 'commits(train).txt --keep-sequence --stoplist-file ../stoplists/poisson_stopwords.txt --output ' + TM_OUTPUT_PATH + '/train_corpus.mallet')
    elif type == 'RAKE':
        cmd_result = os.system('mallet import-file --input ' + TRAIN_NLP_PATH + 'commits(train).txt --keep-sequence --stoplist-file ../stoplists/rake_stopwords.txt --output ' + TM_OUTPUT_PATH + '/train_corpus.mallet')
    elif type == 'AutoGen':
        cmd_result = os.system('mallet import-file --input ' + TRAIN_NLP_PATH + 'commits(train).txt --keep-sequence --stoplist-file ../stoplists/TopClass_extra(' + str(evalNum) + ').txt --output ' + TM_OUTPUT_PATH + '/train_corpus.mallet')
    elif type == 'AutoGenFix':
        cmd_result = os.system('mallet import-file --input ' + TRAIN_NLP_PATH + 'commits(train).txt --keep-sequence --stoplist-file ../stoplists/TopClass_extra.txt --output ' + TM_OUTPUT_PATH + '/train_corpus.mallet')  
    
    if not cmd_result == 0:
        print 'Error..\n'
            
    os.chdir('..')
    
# Topic Modeling 占쎈즼�뵳�덈┛
def runTM4Internal(tryIdx):
    
    os.chdir(CUR_PATH + '/mallet/bin')  
    
    # 1. Making Train corpus to Topic Model
    makeTrainTM(tryIdx)    

    # 2. Making Internal data set corpus to Topic Model
    for sampleIdx in range(1, SAMPLE_NUM+1):
                
        cmd_result = os.system('mallet evaluate-topics --evaluator ' + TM_OUTPUT_PATH + 'evaluator' 
                               ' --input ' + TM_OUTPUT_PATH + 'test_corpus(' + str(sampleIdx) + ').mallet' + 
                               ' --output-doc-probs ' + TM_OUTPUT_PATH + 'docprobs(' + str(sampleIdx) + ').txt')
        
        if not cmd_result == 0:
            print 'Test topic model 占쎈퓠占쎌쑎 獄쏆뮇源�\n'
            exit()
                   
        # Document length �뤃�뗫릭疫뀐옙
        cmd_result = os.system('mallet run cc.mallet.util.DocumentLengths' +
                               ' --input ' + TM_OUTPUT_PATH + 'test_corpus(' + str(sampleIdx) + ').mallet' +
                               ' > ' + TM_OUTPUT_PATH + 'doclengths(' + str(sampleIdx) +').txt')
        
    os.chdir('../..')
    
def runTM4External(tryIdx):
    
    os.chdir(CUR_PATH + '/mallet/bin')  
    
    # 1. Making Train corpus to Topic Model
    makeTrainTM(tryIdx)
    
    # 2. Making External textual corpus to Topic Model
    cmd_result = os.system('mallet evaluate-topics --evaluator ' + TM_OUTPUT_PATH + 'evaluator' 
                               ' --input ' + TM_OUTPUT_PATH + 'external_corpus.mallet' + 
                               ' --output-doc-probs ' + TM_OUTPUT_PATH + 'external_docprobs.txt')
        
    if not cmd_result == 0:
        print 'External test topic model error...'
        exit()
                   
    # 3. Document length calculation...
    cmd_result = os.system('mallet run cc.mallet.util.DocumentLengths' +
                           ' --input ' + TM_OUTPUT_PATH + 'external_corpus.mallet' +
                           ' > ' + TM_OUTPUT_PATH + 'external_doclengths.txt')
    
def makeTrainTM(tryIdx):
    
    os.chdir(CUR_PATH + '/mallet/bin')  
    
    # Making Train File to Topic Model
    cmd_result = os.system('mallet train-topics --input ' + TM_OUTPUT_PATH + 'train_corpus.mallet --num-topics ' + str(TOPIC_NUMBER) +
                             ' --evaluator-filename ' + TM_OUTPUT_PATH + 'evaluator' 
                             ' --output-topic-keys ' + TM_OUTPUT_PATH + 'AssociatedWords(' + str(tryIdx) + '-' + str(TOPIC_NUMBER) + ').csv' + 
                             ' --output-doc-topics ' + TM_OUTPUT_PATH + 'TopicContribution(' + str(TOPIC_NUMBER) + ').csv' +
                             ' --num-iterations 300 --show-topics-interval 1000 ' +
                             ' --num-threads 16')
      
    if not cmd_result == 0:
        print 'Train topic model 占쎈퓠占쎌쑎 獄쏆뮇源�\n'
        exit()
    
    
def calcPerplexity4Internal(evalNum, tryNum): 
    
    OUTPUT_FILE = open(TM_OUTPUT_PATH + 'perplexity(' + str(evalNum) + '-' + str(tryNum) + ').txt', 'w')
        
    # 占쎄묘占쎈탣 test file占쎌벥 Perplexity �④쑴沅�
    sumOfPerplexity = 0
    for tryIdx in range(1, SAMPLE_NUM+1):
    
        logLikelihood   = [float(ll) for ll in open(TM_OUTPUT_PATH + 'docprobs(' + str(tryIdx) + ').txt')]
        docLength       = [int(length) for length in open(TM_OUTPUT_PATH + 'doclengths(' + str(tryIdx) + ').txt')] 
        
        sumOfLL     = sum(logLikelihood)
        sumOfDocLen = sum(docLength)
        perplexity  = math.exp(-sumOfLL / sumOfDocLen)
        sumOfPerplexity += perplexity                                       # 占쎈즸域뱀쥙�뱽 占쎄땀疫뀐옙 占쎌맄占쎈퉸 占쎈�占쎄텦
        
        OUTPUT_FILE.write(str(perplexity) + '\n')
        
    OUTPUT_FILE.write(str(sumOfPerplexity/SAMPLE_NUM) + '\n')
    
    return sumOfPerplexity/SAMPLE_NUM
            
def calcPerplexity4External(approach): 
    
    OUTPUT_FILE = open(TM_OUTPUT_PATH + 'external_perplexity(' + approach + ').txt', 'w')
        
    # 占쎄묘占쎈탣 test file占쎌벥 Perplexity �④쑴沅�
    logLikelihood   = [float(ll) for ll in open(TM_OUTPUT_PATH + 'external_docprobs.txt')]
    docLength       = [int(length) for length in open(TM_OUTPUT_PATH + 'external_doclengths.txt')] 
    
    sumOfLL     = sum(logLikelihood)
    sumOfDocLen = sum(docLength)
    perplexity  = math.exp(-sumOfLL / sumOfDocLen)
        
    OUTPUT_FILE.write(str(perplexity) + '\n')
    OUTPUT_FILE.flush()
    
    return perplexity            

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
            if minSumPMI > sum(PMIMatrix[mRow]):                    # PMI占쎌벥 占쎈�占쎌뵠 占쎌삂占쏙옙 word�몴占� 占쎄퐨占쎄문占쎈퉸占쎄퐣 筌욑옙占쎌뒲占쎈뼄.(占쎌읈筌ｏ옙 占쎈뼊占쎈선占쎈굶�⑨옙 �꽴占쏙옙�졃占쎄쉐占쎌뵠 揶쏉옙占쎌삢 占쎌삂占쎈뼄)
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

def AutoGenStopwords():
    
    for evalNum in range(1, 2):
             
        PerplexityResult = list()
        PERPLEXITY_OUTPUT = open(TM_OUTPUT_PATH + '/AvgPerplexity(' + str(evalNum) + ').txt', 'w')
         
        STOPWORD_FILE = open(CUR_PATH + '/mallet/stoplists/TopClass_extra(' + str(evalNum) + ').txt', 'w') 
              
        randomSelTestfile()
        makeInternalFileBoW()
         
        for tryIdx in range(1,422):
             
            makeTrainFileBoW('AutoGen', evalNum)
            runTM4Internal(tryIdx)
            PerplexityResult.append(str(calcPerplexity4Internal(evalNum, tryIdx)))                  # 占쎈즸域뱄옙 perplexity 獄쏆룄由�
              
            candidateStopwords = calcTopicCoherence(tryIdx)        
            existingStopword = [line.strip() for line in open(CUR_PATH + '/mallet/stoplists/TopClass_extra(' + str(evalNum) + ').txt', 'r')]        
            existingStopword.append(calcTopicCoherece2(candidateStopwords, tryIdx))    # 占쎈꽅占쎈동癰귨옙 stopword占쎈퓠占쎄퐣 占쎈뼄占쎈뻻 1揶쏉옙 筌믩쵐釉섓옙苑� �빊遺쏙옙
                 
            STOPWORD_FILE = open(CUR_PATH + '/mallet/stoplists/TopClass_extra(' + str(evalNum) + ').txt', 'w')
            STOPWORD_FILE.write('\n'.join(existingStopword))            # Extra stopword 占쎈솁占쎌뵬占쎈퓠 占쎈쾺疫뀐옙
            STOPWORD_FILE.flush()
            print existingStopword      
 
        PERPLEXITY_OUTPUT.write('\n'.join(PerplexityResult))   
     
def TM4Evaluation(dataType):
    
    if dataType == 'Internal':
        randomSelTestfile()
        makeInternalFileBoW()
    else:
        makeExternalFileBoW()
                
    for approach in ['Foxlist', 'Poisson', 'RAKE', 'AutoGenFix']:

        PERPLEXITY_OUTPUT = open(TM_OUTPUT_PATH + '/Perplexity(' + approach + ').txt', 'w')
        makeTrainFileBoW(approach, 1)
        
        if dataType == 'Internal':                      
            runTM4Internal(approach)
            PERPLEXITY_OUTPUT.write(str(calcPerplexity4Internal(1, approach)))
        else:   
            for tryIdx in range(1,31):                   
                runTM4External(approach)            
                PERPLEXITY_OUTPUT.write(str(calcPerplexity4External(approach)) + '\n')
                PERPLEXITY_OUTPUT.flush()
            
if __name__ == "__main__":
    
#     AutoGenStopwords()
#     TM4Evaluation('Internal')
    TM4Evaluation('External')

