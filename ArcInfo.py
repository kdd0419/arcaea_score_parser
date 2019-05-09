#!/usr/bin/env python
# coding: utf-8

# ## 개요

# > 내가 좋아하는 리듬 게임이 있는데,
# > 이 게임은 점수를 뽑아올 수 있는 사이트가 있다.
# > 이 사이트에서 곡을 하나씩 찾아 입력해서 점수를 확인 하는 방법은 좀 번거롭다
# > 그래서 이렇게 메크로를 만들어 보았다.

# ## 필요한 모듈 호출

# In[1]:


from bs4 import BeautifulSoup as bs
import requests as req
import json
import csv
import urllib.parse


# ## 게임에서 자신의 아이디 입력


# In[2]:


user_id = input("Input your ID >")


# ## 곡 목록 가져오기


# In[3]:


res = req.get("https://lab.zl-studio.cn/potential/ArcTools/ArcSonglist.json")


# In[4]:


song_dic = json.loads(res.text)['songs']


# In[5]:


song_info = []
for song in song_dic:
    song_tmp = []
    song_tmp.append(song['id'])
    song_tmp.append(song['title_localized']['en'])
    for i in range(3):
        song_tmp.append(
            [song['difficulties'][i]['rating'],
                song['difficulties'][i]['fixedValue']])
    song_info.append(song_tmp)


# ## 크롤링 실행


# In[6]:


RSS = "https://lab.zl-studio.cn/potential/search.php"


# In[7]:


song_rlt_list = []
difficulty = ['PAST', 'PRESENT', 'FUTURE']

for i in range(len(song_info) * 3):
    values = {
        "Aid": user_id, "songid": song_info[i // 3][0], "difficulty": i % 3}
    query = urllib.parse.urlencode(values)
    url = RSS + "?" + query
    res = req.get(url)

    song_dict = {}
    song_dict['song_name'] = song_info[i // 3][1]
    song_dict['difficulty'] = difficulty[i % 3]
    song_dict['level'] = song_info[i // 3][i % 3 + 2][0]
    song_dict['detail_level'] = song_info[i // 3][i % 3 + 2][1]

    if "You hadn't played this song!" in res.text:
        song_dict['played'] = False
        song_rlt_list.append(song_dict)
    else:
        song_dict['played'] = True
        res_dict = json.loads(res.text)

        rows = [
            'score', 'shiny_perfect_count', 'perfect_count',
            'near_count', 'miss_count', 'best_clear_type']
        for i in rows:
            song_dict[i] = res_dict[i]

        song_rlt_list.append(song_dict)

print(song_rlt_list)


# In[8]:


with open('arcaea result.csv', 'w', newline="\n", encoding='utf-8') as csv_f:
    fieldnames = [
        'song_name', 'difficulty', 'level', 'detail_level', 'played',
        'score', 'shiny_perfect_count', 'perfect_count',
        'near_count', 'miss_count', 'best_clear_type'
    ]
    writer = csv.DictWriter(csv_f, fieldnames=fieldnames)
    writer.writeheader()

    for song in song_rlt_list:
        writer.writerow(song)
