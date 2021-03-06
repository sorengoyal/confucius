import xml.etree.ElementTree as ET
import json

# Takes a string of xml that ranker returns, outputs a list of dictionaries describing each returned result
def parseRanker(xml):
    root = ET.fromstring(xml)
    result = []

    for doc in root[1]:
        ans = doc[0][0].text.replace("'", '"').replace('\\xa0', ' ')

        dic = {}
        dic['body'] = json.loads(ans)['answer']
        dic['id'] = doc[1].text
        dic['version'] = doc[2].text
        dic['score'] = doc[3].text
        dic['vector'] = doc[4].text
        dic['confidence'] = doc[5].text

        result.append(dic)

    return result
