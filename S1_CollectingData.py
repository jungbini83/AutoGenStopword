# -*- encoding:utf-8-*- 
import os, re, string, subprocess
from dateutil import parser

def collectCommitLogs(PROJECT_LIST):
    
    CUR_PATH = os.getcwd()
    
    LOG_PATH = CUR_PATH + '/LogHistory/'
    if not os.path.exists(LOG_PATH):
        os.makedirs(LOG_PATH)
        
    for project in PROJECT_LIST:
        
        PROJECT_PATH = CUR_PATH + '/projects/' + project               # �봽濡쒖젥�듃 �뵒�젆�넗由�
        os.chdir(PROJECT_PATH)
        
        OUT_TRAIN_FILE = open(LOG_PATH + project + '(train).txt', 'w')
        OUT_TEST_FILE = open(LOG_PATH + project + '(test).txt', 'w')
        
        for year in range(2012, 2017):                                  # 理쒓렐 5�뀈媛꾩쓽 濡쒓렇 �뜲�씠�꽣 �닔
            
            print "Collecting " + project + "'s " + str(year) + " log history..."
             
            fd_popen = subprocess.Popen('git log --all -p --since="01-Jan-' + str(year) + '" --until="31-Dec-' + str(year) + '"',      # 1�뀈 �떒�쐞濡� �닔吏�
                                        stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
            cmd_result = fd_popen.communicate('')[0]
            
            if year == 2016:
                OUT_TEST_FILE.write(cmd_result)
            else:
                OUT_TRAIN_FILE.write(cmd_result)                        
            
        OUT_TRAIN_FILE.close()
        
def parseLogMessage(PROJECT_LIST, type):
    
    CUR_PATH = os.getcwd()    
    DOC_PATH    = CUR_PATH + '/LogHistory/'
    OUTPUT_PATH = CUR_PATH + '/parsedData/'    
    LOG_PATH    = OUTPUT_PATH + '/Commits/' + type + '/'
    REVFILE_PATH   = OUTPUT_PATH + '/RevsOfCommits/' + type + '/'    
    
    re_commitStart  = re.compile('(commit)\s(.*)(\n)')                       # Commit number �뙣�꽩
    re_revStart     = re.compile('(Date:\s+)(.*)(\n)')                      # revision�씠 �떆�옉�븯�뒗 �뙣�꽩
    re_fileStart    = re.compile('(diff --git)\s(.*)\s(.*)\n')              # revision ���긽 �뙆�씪 �뙣�꽩
    re_revnumStart  = re.compile('(index\s)(.*)(\.\.)(.*)\s([0-9]+)')       # �빐�떦 �뙆�씪�쓽 由щ퉬�쟾 踰덊샇 �뙣�꽩
        
    for program in PROJECT_LIST:
        
        if not os.path.exists(REVFILE_PATH + program):
            os.makedirs(REVFILE_PATH + program)
        if not os.path.exists(LOG_PATH + program):
            os.makedirs(LOG_PATH + program)
        
        fileName            = ''                                            # �뙆�씪紐�
        buggyRevisionNum    = ''                                            # buggy revision 踰덊샇
        cleanRevisionNum    = ''                                            # clean revision 踰덊샇
        commitNum           = ''                                            # Commit number
        commitMsg           = ''                                            # Commit Message    
        commitDate          = ''                                            # commit�씠 �닔�뻾�맂 �궇吏�  
        isCommitMsg         = False                                         # Commit Message�씠�깘?      
        for line in open(DOC_PATH + program + '(' + type + ').txt', 'r'):  
            
            line = filter(lambda x: x in string.printable, line)
            
            if line == '\r\n':      continue
            
            if isCommitMsg:
                commitMsg += ' ' + line.strip()                             # Commit Message �늻�쟻
            
            match_commitStart   = re_commitStart.match(line)
            if match_commitStart:
                
                # �깉濡쒖슫 commit�씠 �떆�옉�븯誘�濡� 洹몄쟾源뚯��쓽 �뙆�씪由ъ뒪�듃�뒗 ���옣
                if fileName != '' and '.java' in fileName:                  # �떎瑜� 由щ퉬�쟾�쓽 �떆�옉�씠誘�濡� 洹몄쟾 file�� 湲곕줉�븯湲�
                    print program + ':' + fileName
                    
                    OUT_FILE = open(REVFILE_PATH + program + '/[' + commitDate + ']' + commitNum + '.txt', 'a')                                                                     
                    OUT_FILE.write(fileName + ',' + buggyRevisionNum + ',' + cleanRevisionNum + '\n')
                    
                    OUT_FILE.flush()
                    
                    fileName = ''
                
                commitNum = match_commitStart.group(2)
                commitNum = commitNum[:7]
                isCommitMsg = False
                
            match_revStart       = re_revStart.match(line)                      # Revision�쓽 �떆�옉 遺�遺�            
            if match_revStart:
                
                commitDate = match_revStart.group(2)
                dateObj = parser.parse(' '.join(commitDate.split(' ')[:-1])) 
                commitDate = dateObj.date().isoformat()
                
                isCommitMsg = True
                continue
            
            match_fileStart      = re_fileStart.match(line)
            if match_fileStart:
                
                # �씪�떒 �궇吏쒖� 湲곕줉�맂 Commit log瑜� �벐怨� �떆�옉
                if isCommitMsg:
                    
                    if 'commit' in commitMsg:
                        commitMsg = commitMsg[commitMsg.index('commit')+48:commitMsg.index('diff')]
                    elif 'diff' in commitMsg:
                        commitMsg = commitMsg[:commitMsg.index('diff')]
                                        
                    LOGDocFile = open(LOG_PATH + program + '/[' + commitDate + ']' + commitNum + '.txt', 'a')           # topic modeling�쓣 �쐞�빐 濡쒓렇 硫붿떆吏� �뵲濡� 蹂닿�
                    LOGDocFile.write(commitMsg)
                    LOGDocFile.flush()
                    
                    commitMsg = ''
                    isCommitMsg = False                
                                       
                # fileName�씠 鍮덉뭏�씠 �븘�땲硫� �삉 �떎瑜� revision�씠 �깉濡� �떆�옉�븯誘�濡� 湲곗〈 revision 湲곕줉�븯湲�
                if fileName != '' and '.java' in fileName:             
                    print program + ':' + fileName                                                 
                    
                    OUT_FILE = open(REVFILE_PATH + program + '/[' + commitDate + ']' + commitNum + '.txt', 'a')                                                                     
                    OUT_FILE.write(fileName + ',' + buggyRevisionNum + ',' + cleanRevisionNum + '\n')
                    
                    OUT_FILE.flush()
                
                fileName = match_fileStart.group(2).strip()
                fileName = fileName[fileName.rfind('/')+1:]
                                    
                continue
            
            match_revnumStart   = re_revnumStart.match(line)
            if match_revnumStart:
                if '.java' in fileName:            
                    buggyRevisionNum = match_revnumStart.group(2)
                    cleanRevisionNum = match_revnumStart.group(4)
                continue
            
        # 留덉�留� revision �젙蹂닿퉴吏� 湲곕줉�븯怨� �걹�궡湲�        
        if fileName != '' and '.java' in fileName:                                              
            OUT_FILE = open(LOG_PATH + program + '/[' + commitDate + ']' + commitNum + '.txt', 'a')                                                                     
            OUT_FILE.write(REVFILE_PATH + ',' + buggyRevisionNum + ',' + cleanRevisionNum + '\n')
            OUT_FILE.close ()     

if __name__ == "__main__":
    
    PROJECT_LIST = ['kotlin','gradle','orientdb','PDE','Actor','hadoop','Graylog','cassandra','CoreNLP','netty','druid','alluxio']
        
    #collectCommitLogs(PROJECT_LIST)
    parseLogMessage(PROJECT_LIST, 'train')
    parseLogMessage(PROJECT_LIST, 'test')