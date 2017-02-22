# -*- encoding:utf-8-*-
import os, math, random, shutil
import S3_CalcPMI

CUR_PATH = os.getcwd()
PREPROCESS_PATH = CUR_PATH + '/TermFrequency/'
INPUT_PATH = CUR_PATH + '/parsedData/'
TRAIN_NLP_PATH = INPUT_PATH + '/TrainCommits/'
TEST_NLP_PATH = INPUT_PATH + '/TestCommits/'
SAMPLE_DOC_PATH = CUR_PATH + '/sampleDoc/'
TM_OUTPUT_PATH = CUR_PATH + '/TMOutput/'

if not os.path.exists(TM_OUTPUT_PATH):
    os.makedirs(TM_OUTPUT_PATH)

def makeTestFileBoW():
    
    os.chdir(CUR_PATH + '/mallet/bin/')  
    
    for tryIdx in range(1, 11):                                                     # 10번 sample 파일을 랜덤으로 추출
    
        # Test 파일 리스트에서 파일을 랜덤으로 추출
        testFileList = list()
        for path, dir, files in os.walk(TRAIN_NLP_PATH):
            testFileList.extend([path + '/' + fileName for fileName in files])
        
        sampleDoc = random.sample(testFileList, 2000)                               # 전체 문서의 20%를 선택
    
        if os.path.exists(SAMPLE_DOC_PATH):
            shutil.rmtree(SAMPLE_DOC_PATH)                                              # 먼저 기존 샘플파일 지우기    
        if not os.path.exists(SAMPLE_DOC_PATH):
            os.makedirs(SAMPLE_DOC_PATH)
            
        fileIdx = 1
        for filePath in sampleDoc:
            print '#' + str(tryIdx) + ' Sample [' + str(fileIdx) + '/2000] copying filename is \'' + filePath + '\'.'
            shutil.copy(filePath, SAMPLE_DOC_PATH)
            fileIdx+=1
                
        print '프로그램 별 Test용 Basket of Words 만들기'
        cmd_result = os.system('mallet import-dir --input ' + SAMPLE_DOC_PATH + ' --remove-stopwords --keep-sequence --output ' + TM_OUTPUT_PATH + '/test_corpus(' + str(tryIdx) + ').mallet')
        if not cmd_result == 0:
            print 'Error..\n'
            
    os.chdir('..')

def makeTrainFileBoW():
    
    os.chdir(CUR_PATH + '/mallet/bin/')
    
    # Train용 corpus 만들기
    print 'Train용 Basket of Words 만들기'
    cmd_result = os.system('mallet import-file --input ' + TRAIN_NLP_PATH + 'commits(train).txt --remove-stopwords --keep-sequence --extra-stopwords ../stoplists/TopClass_extra.txt --output ' + TM_OUTPUT_PATH + '/train_corpus.mallet')
    if not cmd_result == 0:
        print 'Error..\n'
            
    os.chdir('..')
    
# Topic Modeling 돌리기
def runTM():
    
    os.chdir(CUR_PATH + '/mallet/bin')  
    
    for topicK in TOPIC_NUMBER:
    
        # 1. Train File 모델링
        cmd_result = os.system('mallet train-topics --input ' + TM_OUTPUT_PATH + 'train_corpus.mallet --num-topics ' + str(topicK) +
                                 ' --evaluator-filename ' + TM_OUTPUT_PATH + 'evaluator' 
                                 ' --output-topic-keys ' + TM_OUTPUT_PATH + 'AssociatedWords(' + str(topicK) + ').csv' + 
                                 ' --output-doc-topics ' + TM_OUTPUT_PATH + 'TopicContribution(' + str(topicK) + ').csv' +
                                 ' --num-iterations 1000 --show-topics-interval 1000 --optimize-interval 20' +
                                 ' --num-threads 16 --random-seed 0')
          
        if not cmd_result == 0:
            print 'Train topic model 에러 발생\n'
            exit()
        
        # 2. 샘플 Test File 모델링
        for tryIdx in range(1, 11):
                    
            cmd_result = os.system('mallet evaluate-topics --evaluator ' + TM_OUTPUT_PATH + 'evaluator' 
                                   ' --input ' + TM_OUTPUT_PATH + 'test_corpus(' + str(tryIdx) + ').mallet' + 
                                   ' --output-doc-probs ' + TM_OUTPUT_PATH + 'docprobs(' + str(tryIdx) + ').txt')
            
            if not cmd_result == 0:
                print 'Test topic model 에러 발생\n'
                exit()
                       
            # Document length 구하기
            cmd_result = os.system('mallet run cc.mallet.util.DocumentLengths' +
                                   ' --input ' + TM_OUTPUT_PATH + 'test_corpus(' + str(tryIdx) + ').mallet' +
                                   ' > ' + TM_OUTPUT_PATH + 'doclengths(' + str(tryIdx) +').txt')
        
    os.chdir('../..')
    
def calcPerplexity(tryNum): 
    
    OUTPUT_FILE = open(TM_OUTPUT_PATH + 'perplexity(' + str(tryNum) + ').txt', 'w')
        
    # 샘플 test file의 Perplexity 계산
    for tryIdx in range(1, 11):
    
        logLikelihood   = [float(ll) for ll in open(TM_OUTPUT_PATH + 'docprobs(' + str(tryIdx) + ').txt')]
        docLength       = [int(length) for length in open(TM_OUTPUT_PATH + 'doclengths(' + str(tryIdx) + ').txt')] 
        
        sumOfLL     = sum(logLikelihood)
        sumOfDocLen = sum(docLength)
        
        OUTPUT_FILE.write(str(math.exp(-sumOfLL / sumOfDocLen)) + '\n')    
            
def calcTopicCoherence():
    
    STOPWORD_FILE = open(CUR_PATH + '/mallet/stoplists/TopClass_extra.txt', 'a')
        
    for topicK in TOPIC_NUMBER:
        
        row, col = topicK, topicK
        PMIMatrix = [[0 for x in range(col)] for y in range(row)]
            
        topicNum = 0
        for line in open(TM_OUTPUT_PATH + '/AssociatedWords(' + str(topicK) + ').csv'):            
     
            topicWords = line.split()[2:12]
     
            for mRow in range(0, len(topicWords)-1):
                
                for mCol in range(mRow+1, len(topicWords)):
                        
                    #pmiValue = S3_CalcPMI.calcPMI(topicWords[mRow],topicWords[mCol])
                    pmiValue = S3_CalcPMI.calcPMIfromFile(topicWords[mRow],topicWords[mCol])
                            
                    print "[Topic" + str(topicNum) + "] PMI value between " + topicWords[mRow] + " and " + topicWords[mCol] + ": " + str(pmiValue)
                    PMIMatrix[mRow][mCol] = pmiValue
                    PMIMatrix[mCol][mRow] = pmiValue
                                
            topicNum += 1
            
            for mRow in range(0,len(PMIMatrix)):
                print PMIMatrix[mRow]
                
            minIdx = -1
            minSumPMI = 1000
            for mRow in range(0,len(PMIMatrix)):
                if minSumPMI > sum(PMIMatrix[mRow]):                    # PMI의 합이 작은 word를 선택해서 지운다.(전체 단어들과 관련성이 가장 작다)
                    minIdx = mRow
            
            print topicWords[minIdx] + ' added to stopword.'
            STOPWORD_FILE.write(topicWords[minIdx] + '\n')
            STOPWORD_FILE.flush()           
    
if __name__ == "__main__":
    
    PROJECT_LIST = ['kotlin','gradle','orientdb','PDE','Actor','hadoop','Graylog','cassandra','CoreNLP','netty','druid','alluxio']
    TOPIC_NUMBER = [10]

#     makeTestFileBoW()
#     makeTrainFileBoW()
#     runTM()
#     calcPerplexity(1)
for tryIdx in range(2,11):
    calcTopicCoherence()
    makeTrainFileBoW()
    runTM()
    calcPerplexity(tryIdx)