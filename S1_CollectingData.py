# -*- encoding:utf-8-*- 
import os, re, string, subprocess
from dateutil import parser

def collectCommitLogs(PROJECT_LIST):
    
    CUR_PATH = os.getcwd()
    
    LOG_PATH = CUR_PATH + '/LogHistory/'
    if not os.path.exists(LOG_PATH):
        os.makedirs(LOG_PATH)
        
    for project in PROJECT_LIST:
        
        PROJECT_PATH = CUR_PATH + '/projects/' + project               
        os.chdir(PROJECT_PATH)
        
        OUT_TRAIN_FILE = open(LOG_PATH + project + '(train).txt', 'w')
        OUT_TEST_FILE = open(LOG_PATH + project + '(test).txt', 'w')
        
        for year in range(2012, 2017):                                  
            
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
    
    re_commitStart  = re.compile('(commit)\s(.*)(\n)')                      
    re_revStart     = re.compile('(Date:\s+)(.*)(\n)')                      
    re_fileStart    = re.compile('(diff --git)\s(.*)\s(.*)\n')              
    re_revnumStart  = re.compile('(index\s)(.*)(\.\.)(.*)\s([0-9]+)')       
        
    for program in PROJECT_LIST:
        
        if not os.path.exists(REVFILE_PATH + program):
            os.makedirs(REVFILE_PATH + program)
        if not os.path.exists(LOG_PATH + program):
            os.makedirs(LOG_PATH + program)
        
        fileName            = ''                                            
        buggyRevisionNum    = ''                                            # buggy revision
        cleanRevisionNum    = ''                                            # clean revision
        commitNum           = ''                                            # Commit number
        commitMsg           = ''                                            # Commit Message    
        commitDate          = ''                                            
        isCommitMsg         = False                                         
        for line in open(DOC_PATH + program + '(' + type + ').txt', 'r'):  
            
            line = filter(lambda x: x in string.printable, line)
            
            if line == '\r\n':      continue
            
            if isCommitMsg:
                commitMsg += ' ' + line.strip()                             
            
            match_commitStart   = re_commitStart.match(line)
            if match_commitStart:
                
                if fileName != '' and '.java' in fileName:                 
                    print program + ':' + fileName
                    
                    OUT_FILE = open(REVFILE_PATH + program + '/[' + commitDate + ']' + commitNum + '.txt', 'a')                                                                     
                    OUT_FILE.write(fileName + ',' + buggyRevisionNum + ',' + cleanRevisionNum + '\n')
                    
                    OUT_FILE.flush()
                    
                    fileName = ''
                
                commitNum = match_commitStart.group(2)
                commitNum = commitNum[:7]
                isCommitMsg = False
                
            match_revStart       = re_revStart.match(line)                            
            if match_revStart:
                
                commitDate = match_revStart.group(2)
                dateObj = parser.parse(' '.join(commitDate.split(' ')[:-1])) 
                commitDate = dateObj.date().isoformat()
                
                isCommitMsg = True
                continue
            
            match_fileStart      = re_fileStart.match(line)
            if match_fileStart:
                
                if isCommitMsg:
                    
                    if 'commit' in commitMsg:
                        commitMsg = commitMsg[commitMsg.index('commit')+48:commitMsg.index('diff')]
                    elif 'diff' in commitMsg:
                        commitMsg = commitMsg[:commitMsg.index('diff')]
                                        
                    LOGDocFile = open(LOG_PATH + program + '/[' + commitDate + ']' + commitNum + '.txt', 'a')          
                    LOGDocFile.write(commitMsg)
                    LOGDocFile.flush()
                    
                    commitMsg = ''
                    isCommitMsg = False                
                
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
        
        if fileName != '' and '.java' in fileName:                                              
            OUT_FILE = open(LOG_PATH + program + '/[' + commitDate + ']' + commitNum + '.txt', 'a')                                                                     
            OUT_FILE.write(REVFILE_PATH + ',' + buggyRevisionNum + ',' + cleanRevisionNum + '\n')
            OUT_FILE.close ()     

if __name__ == "__main__":
    
    PROJECT_LIST = ['kotlin','gradle','orientdb','PDE','Actor','hadoop','Graylog','cassandra','CoreNLP','netty','druid','alluxio']
        
    collectCommitLogs(PROJECT_LIST)
    parseLogMessage(PROJECT_LIST, 'train')
    parseLogMessage(PROJECT_LIST, 'test')
