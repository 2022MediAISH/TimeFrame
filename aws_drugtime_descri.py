import datetime
from operator import length_hint
import requests
import re
from word2number import w2n
import boto3
import json

url = "https://www.clinicaltrials.gov/api/query/full_studies?expr=Effect+of+Hydralazine+on+Alzheimer%27s+Disease+%28EHSAN%29&min_rnk=1&max_rnk=1&fmt=json"
response = requests.get(url).json()
detail_description = ""
brief_description = ""
drug_list = response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['ArmsInterventionsModule']['InterventionList']['Intervention']
try:
    detail_description = response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['DescriptionModule']["BriefSummary"]
except KeyError:
    print("")
try:
    brief_description = response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['DescriptionModule']["DetailedDescription"]
except KeyError:
    print("")

#print(detail_description)
#print(drug_list)

drug = []
time = []
time_set = []
time_label = ['day','days','week','weeks','month','year']
time_label2 = ['day','week','month','year']
drug_date = []
left = 0
right = 0

drug_dict = {}

for i in range(len(drug_list)):
    drug.append(drug_list[i]['InterventionName'])
    drug_dict[drug_list[i]['InterventionName'].lower()] = ""
#print(drug)


slpit = detail_description.replace(",", "").split(". ") + brief_description.replace(",", "").split(".")

for i1 in range(len(slpit)):    
    temp = slpit[i1].split()
    #print(temp)
    #print(slpit[i1])
    for i2 in range(len(drug)):
        if drug[i2]+ ' ' in slpit[i1]:
            #print(slpit[i1])
            drug_index = temp.index(drug[i2])
            #print(drug_index)
            #print(temp[drug_index])
            for i5 in range(len(time_label)):
                for i3 in range(drug_index-1, -1, -1):
                    if time_label[i5] == temp[i3]:
                        left = i3
                        break
                for i4 in range(drug_index, len(temp)):
                    if time_label[i5] == temp[i4]:
                        right = i4
                        break
            #print(left , right)
            if left == 0 and right == 0:
                continue
            elif left == 0 or abs(drug_index - left) >= abs(drug_index - right):
                drug_date.append(temp[drug_index : right + 1])
                drug_dict[temp[drug_index].lower()] = temp[right - 1] + " " + temp[right]
            elif right == 0 or abs(drug_index - left) < abs(drug_index - right):
                drug_date.append(temp[left-1 :drug_index  + 1])
                drug_dict[temp[drug_index].lower()] = temp[left - 1] + " " + temp[left]
            left = 0
            right = 0
            #print("--------------------------------------------")
            
        elif drug[i2].lower() + ' ' in slpit[i1]:
            #print(slpit[i1])
            drug_index = temp.index(drug[i2].lower())
            #print(drug_index)
            #print(temp[drug_index])
            for i5 in range(len(time_label)):
                for i3 in range(drug_index-1, -1, -1):
                    if time_label[i5] == temp[i3]:
                        left = i3
                        break
                for i4 in range(drug_index, len(temp)):
                    if time_label[i5] == temp[i4]:
                        right = i4
                        break
            #print(left , right)
            if left == 0 and right == 0:
                continue
            elif left == 0 or abs(drug_index - left) >= abs(drug_index - right):
                drug_date.append(temp[drug_index : right + 1])
                drug_dict[temp[drug_index]] = temp[right - 1] + " " + temp[right]    
            elif right == 0 or abs(drug_index - left) < abs(drug_index - right):
                drug_date.append(temp[left :drug_index  + 1])
                drug_dict[temp[drug_index]] = temp[left - 1] + " " + temp[left]
            left = 0
            right = 0
#print(drug_date)
print(drug_dict)



#---------------------------------여기까지가 그냥 description관련된 코드

comprehend = boto3.client('comprehend')

DetectEntitiestext = detail_description
test = (comprehend.detect_entities(Text=DetectEntitiestext, LanguageCode='en'))


protocolsection = response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']

index2 = 0
for value in protocolsection['ArmsInterventionsModule']['InterventionList']['Intervention']:
    for i in drug_dict:
        #print(i)
        #print(value["InterventionName"])
        if i == value["InterventionName"].lower():
            DetectEntitiestext = value['InterventionDescription']
            #print(DetectEntitiestext)
            test = (comprehend.detect_entities(Text=DetectEntitiestext, LanguageCode='en'))
            with open("name" + str(index2)  +".json", 'w') as json_file:
                
                json.dump(test, json_file, sort_keys=True, indent=4)
            with open("name" + str(index2)+".json", "r") as read_file:
                index2= index2+1
                data = json.load(read_file)
                for i2 in range(len(data['Entities'])):
                    #print("요기있지욜")
                    #print(data['Entities'][i2]['Text'])
                    for j in range(len(time_label2)):
                        #print("조기있지욜")
                        #print(time_label2[j])
                        if time_label2[j] in data['Entities'][i2]['Text']:
                            drug_dict[i.lower()] = data['Entities'][i2]['Text']
                #print(time)
print(drug_dict)

#------------------------------------------이제 각 실험군끼리 연결 시키는 부분

# for value in protocolsection['ArmsInterventionsModule']['ArmGroupList']['ArmGroup']:
#     for index3 in drug_dict:
