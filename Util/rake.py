# -*- encoding:utf-8-*-
# Implementation of RAKE - Rapid Automtic Keyword Exraction algorithm
# as described in:
# Rose, S., D. Engel, N. Cramer, and W. Cowley (2010). 
# Automatic keyword extraction from indi-vidual documents. 
# In M. W. Berry and J. Kogan (Eds.), Text Mining: Applications and Theory.unknown: John Wiley and Sons, Ltd.

import re, os
import operator
from operator import itemgetter
from collections import OrderedDict

debug = False
test = False


def is_number(s):
    try:
        float(s) if '.' in s else int(s)
        return True
    except ValueError:
        return False


def load_stop_words(stop_word_file):
    """
    Utility function to load stop words from a file and return as a list of words
    @param stop_word_file Path and file name of a file containing stop words.
    @return list A list of stop words.
    """
    stop_words = []
    for line in open(stop_word_file):
        if line.strip()[0:1] != "#":
            for word in line.split():  # in case more than one per line
                stop_words.append(word)
    return stop_words


def separate_words(text, min_word_return_size):
    """
    Utility function to return a list of all words that are have a length greater than a specified number of characters.
    @param text The text that must be split in to words.
    @param min_word_return_size The minimum no of characters a word must have to be included.
    """
    splitter = re.compile('[^a-zA-Z0-9_\\+\\-/]')
    words = []
    for single_word in splitter.split(text):
        current_word = single_word.strip().lower()
        #leave numbers in phrase, but don't count as words, since they tend to invalidate scores of their phrases
        if len(current_word) > min_word_return_size and current_word != '' and not is_number(current_word):
            words.append(current_word)
    return words


def split_sentences(text):
    """
    Utility function to return a list of sentences.
    @param text The text that must be split in to sentences.
    """
    sentence_delimiters = re.compile(u'[.!?,;:\t\\\\"\\(\\)\\\'\u2019\u2013]|\\s\\-\\s')
    sentences = sentence_delimiters.split(text)
    return sentences


def build_stop_word_regex(stop_word_file_path):
    stop_word_list = load_stop_words(stop_word_file_path)
    stop_word_regex_list = []
    for word in stop_word_list:
        word_regex = r'\b' + word + r'(?![\w-])'  # added look ahead for hyphen
        stop_word_regex_list.append(word_regex)
    stop_word_pattern = re.compile('|'.join(stop_word_regex_list), re.IGNORECASE)
    return stop_word_pattern


def generate_candidate_keywords(sentence_list, stopword_pattern):
    phrase_list = []
    for s in sentence_list:
        tmp = re.sub(stopword_pattern, '|', s.strip())
        phrases = tmp.split("|")
        for phrase in phrases:
            phrase = phrase.strip().lower()
            if phrase != "":
                phrase_list.append(phrase)
    return phrase_list


def calculate_word_scores(phraseList):
    word_frequency = {}
    word_degree = {}
    for phrase in phraseList:
        word_list = separate_words(phrase, 0)
        word_list_length = len(word_list)
        word_list_degree = word_list_length - 1
        #if word_list_degree > 3: word_list_degree = 3 #exp.
        for word in word_list:
            word_frequency.setdefault(word, 0)
            word_frequency[word] += 1
            word_degree.setdefault(word, 0)
            word_degree[word] += word_list_degree  #orig.
            #word_degree[word] += 1/(word_list_length*1.0) #exp.
    for item in word_frequency:
        word_degree[item] = word_degree[item] + word_frequency[item]

    # Calculate Word scores = deg(w)/frew(w)
    word_score = {}
    for item in word_frequency:
        word_score.setdefault(item, 0)
        word_score[item] = word_degree[item] / (word_frequency[item] * 1.0)  #orig.
    #word_score[item] = word_frequency[item]/(word_degree[item] * 1.0) #exp.
    return word_score

def cacluate_word_freq(phraseList):
    word_frequency = {}
    for phrase in phraseList:
        
        word_list = separate_words(phrase, 0)        
        for word in word_list:
            word_frequency.setdefault(word, 0)
            word_frequency[word] += 1
            
    return word_frequency

def generate_candidate_keyword_scores(phrase_list, word_score):
    keyword_candidates = {}
    for phrase in phrase_list:
        keyword_candidates.setdefault(phrase, 0)
        word_list = separate_words(phrase, 0)
        candidate_score = 0
        for word in word_list:
            candidate_score += word_score[word]
        keyword_candidates[phrase] = candidate_score
    return keyword_candidates


class Rake(object):
    def __init__(self, stop_words_path):
        self.stop_words_path = stop_words_path
        self.__stop_words_pattern = build_stop_word_regex(stop_words_path)

    def run(self, text):
        sentence_list = split_sentences(text)

        phrase_list = generate_candidate_keywords(sentence_list, self.__stop_words_pattern)

        word_scores = calculate_word_scores(phrase_list)

        keyword_candidates = generate_candidate_keyword_scores(phrase_list, word_scores)

        sorted_keywords = sorted(keyword_candidates.iteritems(), key=operator.itemgetter(1), reverse=True)
        return sorted_keywords

def calcuate_rake(filePath):
    
    curPath = os.getcwd()
    OUTPUT_FILE = open(curPath + '/rake.txt', 'w')
    
    word_frequency = {}
    kfDict = {}
    afDict= {}
    for line in open(filePath, 'r'):
                    
        sentenceList = split_sentences(line)            
        
        stoppath = "emptyStoplist.txt"  
        stopwordpattern = build_stop_word_regex(stoppath)
        phraseList = generate_candidate_keywords(sentenceList, stopwordpattern)
        
        # 각 단어 점수 계산
        wordscores = calculate_word_scores(phraseList)

        # 후보 키워드 점수 합산
        keywordcandidates = generate_candidate_keyword_scores(phraseList, wordscores)
        
        # 키워드 정렬
        sortedKeywords = sorted(keywordcandidates.iteritems(), key=operator.itemgetter(1), reverse=True)
        totalKeywords = len(sortedKeywords)
        
        keywordList = [keywordItem[0] for keywordItem in sortedKeywords[0:(totalKeywords / 3)]]
        
        for phrase in phraseList:        
            word_list = separate_words(phrase, 0)        
            for word in word_list:
                word_frequency.setdefault(word, 0)
                word_frequency[word] += 1
                
                if keywordList:
                    if word in keywordList:                                # 1/3 keyword 안에 있다면, 키워드 단어로 간주하고 kf 증가
                        kfDict.setdefault(word, 0)
                        kfDict[word] += 1                            
                    else:
                                         
                        for keyword in keywordList:
                            
                            keywordIdx = phraseList.index(keyword)           # raw text에서 키워드 위치 알아내기
                            
                            if 0 < keywordIdx or keywordIdx < len(phraseList)-1:

                                
                                if 0 < keywordIdx:
                                    leftPhrase = phraseList[keywordIdx-1]                                    
                                    left_word_list = separate_words(leftPhrase, 0)
                                    
                                    if left_word_list:
                                        if word == left_word_list[-1]:
                                            afDict.setdefault(word, 0)                  # 키워드 앞 뒤 단어가 해당 word라면 인접 단어로 간주하고 af 증가
                                            afDict[word] += 1
                                    
                                if keywordIdx < len(phraseList) - 1: 
                                    rightPhrase = phraseList[keywordIdx+1]                                        
                                    right_word_list = separate_words(rightPhrase, 0)
                                    
                                    if right_word_list:                                        
                                        if word == right_word_list[0]:
                                            afDict.setdefault(word, 0)                  # 키워드 앞 뒤 단어가 해당 word라면 인접 단어로 간주하고 af 증가
                                            afDict[word] += 1
                                                    
    sorted_tf = OrderedDict(sorted(word_frequency.items(), key=lambda x: x[1], reverse=True))
                    
    OUTPUT_FILE.write('term,tf,af,kf\n')
    for wordItem, freq in sorted_tf.items():
        
        if not wordItem in afDict:
            afDict.setdefault(wordItem, 0)
        if not wordItem in kfDict:
            kfDict.setdefault(wordItem, 0)
        
        OUTPUT_FILE.write(wordItem + ',' + str(freq) + ',' + str(afDict[wordItem]) + ',' + str(kfDict[wordItem]) + '\n')

if test:
    text = "Merge branch 'staging'  Conflicts: actor-apps/app-desktop/build.sh actor-apps/app-ios/ActorApp.xcodeproj/project.pbxproj actor-apps/app-ios/ActorApp/AppDelegate.swift actor-apps/app-ios/ActorApp/Controllers/Auth/AuthPhoneViewController.swift actor-apps/app-ios/ActorApp/Controllers/Auth/AuthSmsViewController.swift actor-apps/app-ios/ActorApp/Controllers/Discover/DiscoverViewController.swift actor-apps/app-ios/ActorApp/Controllers/Settings/SettingsPrivacyViewController.swift actor-apps/app-ios/ActorApp/Controllers/Settings/SettingsViewController.swift actor-apps/app-ios/ActorApp/Resources/AppTheme.swift actor-apps/app-ios/ActorApp/Supporting Files/ActorApp-Bridging-Header.h actor-apps/app-ios/ActorApp/View/BigPlaceholderView.swift actor-apps/app-ios/ActorApp/View/UATableData.swift actor-apps/app-ios/ActorCore/Config.swift actor-apps/app-ios/ActorCore/Conversions.swift actor-apps/app-ios/Podfile actor-apps/build-tools/ios-build.sh actor-server/actor-core/src/main/protobuf/dialog.proto actor-server/actor-core/src/main/protobuf/user.proto actor-server/actor-core/src/main/scala/im/actor/server/acl/ACLUtils.scala actor-server/actor-core/src/main/scala/im/actor/server/dialog/DialogId.scala actor-server/actor-core/src/main/scala/im/actor/server/dialog/group/GroupDialog.scala actor-server/actor-core/src/main/scala/im/actor/server/dialog/group/GroupDialogHandlers.scala actor-server/actor-core/src/main/scala/im/actor/server/dialog/group/GroupDialogOperations.scala actor-server/actor-core/src/main/scala/im/actor/server/dialog/privat/PrivateDialog.scala actor-server/actor-core/src/main/scala/im/actor/server/dialog/privat/PrivateDialogHandlers.scala actor-server/actor-core/src/main/scala/im/actor/server/dialog/privat/PrivateDialogOperations.scala actor-server/actor-core/src/main/scala/im/actor/server/group/GroupCommandHandlers.scala actor-server/actor-core/src/main/scala/im/actor/server/office/PeerProcessor.scala actor-server/actor-core/src/main/scala/im/actor/server/sequence/SeqUpdatesManager.scala actor-server/actor-core/src/main/scala/im/actor/server/sequence/UpdatesConsumer.scala actor-server/actor-core/src/main/scala/im/actor/server/user/UserCommandHandlers.scala actor-server/actor-core/src/main/scala/im/actor/server/user/UserOffice.scala actor-server/actor-core/src/main/scala/im/actor/server/user/UserProcessor.scala actor-server/actor-enrich/src/main/scala/im/actor/server/enrich/RichMessageWorker.scala actor-server/actor-http-api/src/main/scala/im/actor/server/api/http/HttpApiFrontend.scala actor-server/actor-http-api/src/main/scala/im/actor/server/api/http/webhooks/IngoingHooks.scala actor-server/actor-http-api/src/main/scala/im/actor/server/api/http/webhooks/WebhooksHandler.scala actor-server/actor-notifications/src/main/scala/im/actor/server/notifications/NotificationsSender.scala actor-server/actor-rpc-api/src/main/scala/im/actor/server/api/rpc/service/auth/AuthHelpers.scala actor-server/actor-rpc-api/src/main/scala/im/actor/server/api/rpc/service/auth/AuthServiceImpl.scala actor-server/actor-rpc-api/src/main/scala/im/actor/server/api/rpc/service/configs/ConfigsServiceImpl.scala actor-server/actor-rpc-api/src/main/scala/im/actor/server/api/rpc/service/groups/GroupsServiceImpl.scala actor-server/actor-rpc-api/src/main/scala/im/actor/server/api/rpc/service/messaging/HistoryHandlers.scala actor-server/actor-rpc-api/src/main/scala/im/actor/server/api/rpc/service/messaging/MessagingHandlers.scala actor-server/actor-rpc-api/src/main/scala/im/actor/server/api/rpc/service/webhooks/IntegrationsServiceImpl.scala actor-server/actor-testkit/src/main/scala/im/actor/server/ActorSerializerPrepare.scala actor-server/actor-testkit/src/main/scala/im/actor/server/ServiceSpecHelpers.scala actor-server/actor-tests/src/test/scala/im/actor/server/api/rpc/service/ContactsServiceSpec.scala actor-server/actor-tests/src/test/scala/im/actor/server/http/WebhookHandlerSpec.scala actor-server/project/Build.scala  commit d90fec58914abd958106b1f0451c789c0fff7f9f  fix(web): fix crop avatar minimal width  "

    # 텍스트를 문단으로 구분
    sentenceList = split_sentences(text)
        
    # 비어있는 불용어(stoplist) 사전 적용     
    stoppath = "emptyStoplist.txt"  
    stopwordpattern = build_stop_word_regex(stoppath)

    # 후보 키워드 생성
    phraseList = generate_candidate_keywords(sentenceList, stopwordpattern)
    
    # 각 단어 점수 계산
    wordscores = calculate_word_scores(phraseList)
    
    # 후보 키워드 점수 합산
    keywordcandidates = generate_candidate_keyword_scores(phraseList, wordscores)
    if debug: print keywordcandidates

    # 키워드 정렬
    sortedKeywords = sorted(keywordcandidates.iteritems(), key=operator.itemgetter(1), reverse=True)
    if debug: print sortedKeywords

    totalKeywords = len(sortedKeywords)
    if debug: print totalKeywords
    # print sortedKeywords[0:(totalKeywords / 3)]

    rake = Rake("SmartStoplist.txt")
    keywords = rake.run(text)
    print keywords
    
calcuate_rake("C:/Users/jungbini/git/AutoGenStopword/parsedData/TrainCommits/commits(train).txt")
