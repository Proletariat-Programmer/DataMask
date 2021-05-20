
'''

https://m.diyifanwen.com/zuowen/xiaoxuezuowen/

'''

# {
#             'Category1':[
#                 {
#                     'name':'name',
#                     'article':'string'
#                 },
#                 {
#                     'name':'name1',
#                     'article':'string1'
#                 },
#                 {
#                     'name':'name2',
#                     'article':'string2'
#                 }
#             ]
# }

import re

import requests
from bs4 import BeautifulSoup
import json


Category = []
Category_link = []
names = []
articles = []
primary_articles = {}
i = 0

# Primary_Composition_Category
url3 = 'https://www.diyifanwen.com/zuowen/xiaoxuezuowen/'
response = requests.get(url3)
response.encoding = 'gb2312'
soup = BeautifulSoup(response.text, 'html.parser')
E = soup.find_all(name='a', attrs={"class": "SLmore"})

for item in E:
    x = item.get('href').replace("//", "https://")
    Category_link.append(x)

# print(Category_link)


# Composition_List
for url in Category_link[:2]:
    response = requests.get(url)
    response.encoding = 'gb2312'
    soup = BeautifulSoup(response.text, 'html.parser')
    C = soup.find(id="AListBox")
    D = C.findAll("li")
    kind = soup.h1.text.strip()  # 作文类型
    #Category.append(x)
    #print(x)
    # 作文列表
    for item in D:
        x = item.a.get('href').replace("//", "https://")
        #Composition
        url = x
        response = requests.get(url)
        response.encoding = 'gb2312'
        soup = BeautifulSoup(response.text, 'html.parser')
        A = soup.h1
        B = A.findNextSiblings("p")
        names.append(A.text.strip())
        composition = ''
        for i in B:
            composition += i.text.strip()
        articles.append(composition)
    dic = dict(zip(names, articles))
    primary_articles[kind] = dic
    print(1)

# print(primary_articles)
A_json = json.dumps(primary_articles, ensure_ascii=False)
# print(A_json)
with open("list.json", "w+") as list_file:
    list_file.write(A_json)


# print(Category)
# print(Composition_link)
