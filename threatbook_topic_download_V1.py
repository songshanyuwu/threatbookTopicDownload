#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
文件名：threatbook_topic_download_V1.py
描述：从微步话题获取威胁情报,筛选指定日期，且IOC数量大于0的数据，并下载IOC文件
版本：1.0
作者：songshanyuwu
创建日期：2024年11月13日
"""

import requests
import os
import time
import datetime

def get_compare_date():
    """获取比较日期"""
    compare_dates = input('请输入比较日期，格式为YYYY-MM-DD：')
    if len(compare_dates) == 0:
        compare_dates = time.strftime('%Y-%m-%d', time.localtime())
    return compare_dates

def setup_requests():
    """设置请求的cookies和headers"""
    cookies = {
        'csrfToken': 'xxxxxx请自行替换xxxxxx',
        'sensorsdata2015jssdkcross': 'xxxxxx请自行替换xxxxxx',
        'rememberme': 'xxxxxx请自行替换xxxxxx',
        'xx-csrf': 'xxxxxx请自行替换xxxxxx',
        'day_first': 'true',
        'day_first_activity': 'true',
    }

    headers = {
        'accept': '*/*',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'content-type': 'application/json',
        'priority': 'u=1, i',
        'referer': 'https://x.threatbook.com/v5/topic?q=%23%E6%81%B6%E6%84%8FIP%23',
        'sec-ch-ua': '"Chromium";v="130", "Microsoft Edge";v="130", "Not?A_Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"xxxxxx请自行替换xxxxxx"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'xxxxxx请自行替换xxxxxx',
        'x-csrf-token': 'xxxxxx请自行替换xxxxxx',
        'xx-csrf': 'xxxxxx请自行替换xxxxxx',
    }

    return cookies, headers

def fetch_topic_info_flow(cookies, headers, params):
    """获取话题信息流"""
    url = 'https://x.threatbook.com/v5/node/topic/topicInfoFlow'
    response = requests.get(url, params=params, cookies=cookies, headers=headers)
    return response.json()

def process_article_info(article_info, compare_dates):
    """处理文章信息"""
    ctime = article_info.get('ctime', '--')
    title = article_info.get('title', '-无标题-')
    original_timestamp = ctime 
    topic = article_info.get('topic', '--')
    threat_id = article_info.get('threatId', '--')
    iocCount = article_info.get('iocCount', '0')
    if ctime != '--':
        ctime = datetime.datetime.fromtimestamp(int(ctime / 1000.0)).strftime('%Y-%m-%d')
        if ctime >= compare_dates and iocCount > 0:
            # print(ctime, threat_id, iocCount, topic, title)
            return threat_id, iocCount, original_timestamp, ctime
    return None  # 添加返回值以避免 NoneType 错误

def download_ioc_info(cookies, headers, threat_id, iocCount, original_timestamp, ctime, keyword):
    """下载IOC信息"""
    url = f'https://x.threatbook.com/socialProxy/user/article/downloadIocInfo?shortMessageId={threat_id}'
    headers.pop('x-csrf-token', None)
    headers.pop('content-type', None)
    headers['referer'] = f'https://x.threatbook.com/v5/article?threatInfoID={threat_id}'
    response = requests.get(url, cookies=cookies, headers=headers, stream=True)
    if response.status_code == 200:
        filename = f'ioc_{threat_id}_{iocCount}_{ctime}_{original_timestamp}_{keyword}.xls'
        script_dir = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(script_dir, filename)
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f'-- 文件已下载到：{file_path}')
    else:
        print('请求失败，状态码：', response.status_code)

def main():
    compare_dates = get_compare_date()
    print(f'比较日期为：{compare_dates}')

    # 这里根据需要进行增删
    topics_list = ['#我被攻击了#', '#恶意域名#', '#恶意IP#', '#木马#', '#木马后门#', '#挖矿木马#', '#病毒木马#', '#威胁情报#', '#恶意网站#', '#钓鱼#', '#钓鱼网站#', '#钓鱼邮件#', '#钓鱼网址#', '#钓鱼情报共享#', '#僵尸网络#', '#国外威胁情报#']
    cookies, headers = setup_requests()

    for keyword in topics_list:
        print(f'开始查询话题{keyword}')
        params = {
            'type': 'all',
            'page': '1',
            'pageSize': '10',
            'topic': keyword,
        }
        response_json = fetch_topic_info_flow(cookies, headers, params)

        for node in response_json['data']:
            article_info = node['articleInfo']
            result = process_article_info(article_info, compare_dates)
            if result:  # 检查 result 是否为 None
                threat_id, iocCount, original_timestamp, ctime = result
                download_ioc_info(cookies, headers, threat_id, iocCount, original_timestamp, ctime, keyword)
                time.sleep(10)

if __name__ == '__main__':
    main()
