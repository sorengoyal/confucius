# Parses a Posts.xml file into three input files, for NLC, retrieve, and rank

import json, csv, sys
import xml.etree.ElementTree as ET
import random 
#%%

if __name__ == '__main__':
    docName = sys.argv[1]
    #Create NLC document, retrieve document, ranker csv
    nlc = open(docName + '.nlc.csv', 'w+')
    nlcWrite = csv.writer(nlc)

    retrieveData = {}
    retrieveData['documents'] = []

    rankData = {}

    tree = ET.parse(docName) #opens the input xml file
    root = tree.getroot()

    questions = {} # maps question IDs to question text


    #Foloowing characters are special characters for Ranker. They have to be replaced
    #'\"' (backslash + double quotes)
    #'""' (doubke double quotes)
    #'\n' (newlines)
    for post in root:
        post.attrib['Body'] = post.attrib['Body'].replace('\n', '<br>').replace('"','<dq>').replace('%','<percent>').replace(':','<colon>').replace('\'', '<sq>')#.replace(',','<comma>').replace(' ','<space>')
    #iterate through all row elements children of post element
    for post in root:
        try:
            if post.attrib["PostTypeId"] == '1':  #if post is question
                #add to NLC file

                if len(post.attrib['Body'].encode('utf8')) < 1024:
                    #Was having a unicode issue but solved it with this encode method
                    nlcWrite.writerow(["\"" + post.attrib['Body'].encode('utf8') + "\"", "ai"])


                # Hey tyler, you need to process "post.attrib['Body']"
                questions[post.attrib['Id']] = post.attrib['Body'].encode('utf8')
                rankData[post.attrib['Body'].encode('utf8')] = []

            elif post.attrib["PostTypeId"] == '2': #post is an answer
                parentQ = questions[post.attrib['ParentId']]


                #Added commas between the elements here
                retrieveData['documents'].append({'id': post.attrib['Id'],
                                                  'body': {
                                                    'question' : parentQ ,
                                                    'answer' : post.attrib['Body'].encode('utf8')
                                                  }})

                rankData[parentQ].append((post.attrib['Id'], post.attrib['Score']))
        except Exception:
            continue
    # Create and write to JSON file for retriever
    retriever = open(docName + '.retrieve.json', 'w+')
    json.dump(retrieveData, retriever, indent=4)
    if(len(rankData) > 1500):#Reduce the length of the training data to approx 1500
        ratio = 1500.0/len(rankData)
        print(ratio)
        temp = {}
        for key in rankData:
             if (random.random() < ratio):
                 temp.update({key:rankData[key]})
        rankData = temp
    # Convert rankData to appropriate format and write CSV file
    
    sortedLists = []
    for q in rankData:

        #Had sortedList = rankData[q].sort(key=lambda tup: tup[1], reverse=True)
        #but since the .sort method doesnt return a list I changed it to:
        if rankData[q] != [] :
            sortedList = sorted(rankData[q], key=lambda tup: int(tup[1]), reverse=True)
            answerIds = list(map(lambda tup: tup[0], sortedList))
            answerScores = list(map(lambda tup: tup[1], sortedList))
            answerScores = [x if int(x) > 0 else 0 for x in answerScores]
            row = answerIds + answerScores
            row[::2] = answerIds
            row[1::2] = answerScores
            row.insert(0, q)
            sortedLists.append(row)


    ranker = open(docName + '.ranker.csv', 'w+')
    rankerWrite = csv.writer(ranker, escapechar='\\', quoting=csv.QUOTE_ALL)
    rankerWrite.writerows(sortedLists)
