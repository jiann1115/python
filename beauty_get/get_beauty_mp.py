# get ptt beauty photos in multiprocessing

from bs4 import BeautifulSoup
import requests
import os
import time
import sys
import re
import json
import urllib
from argparse import ArgumentParser

import multiprocessing as mp
from multiprocessing import freeze_support

ptt_url = 'https://www.ptt.cc/'
photo_init_url = "https://i."
jpg_end = ".jpg"
beauty_board_path = 'bbs/Beauty/'
beauty_board = 'bbs/Beauty/index.html'


def get_web_page(url):
    resp = requests.get(
        url=url,
        cookies={'over18': '1'}
    )
    if resp.status_code != 200:
        print('Invalid url:', resp.url)
        return None
    else:
        return resp.text


def get_prev_page_link(dom):
    soup = BeautifulSoup(dom, 'html.parser')
    div = soup.find('div', 'btn-group btn-group-paging')
    btn = div.find('a', 'btn wide')
    for elm in btn.find_next_siblings():
        if elm.string == '‹ 上頁':
            return elm['href']
    return None


def get_articles(dom, date=None):
    soup = BeautifulSoup(dom, 'html.parser')

    articles = []  # 儲存取得的文章資料
    divs = soup.find_all('div', 'r-ent')
    for d in divs:
        if date == None or d.find('div', 'date').string.lstrip() == date:  # post date match
            # 取得推文數
            push_count = 0
            if d.find('div', 'nrec').string:
                try:
                    push_count = 101 if d.find('div', 'nrec').string == '爆' else int(d.find('div', 'nrec').string)
                except ValueError:  # keep 0
                    pass

            # get post title and link
            if d.find('a'):  # post exist if link found
                href = d.find('a')['href']
                title = d.find('a').string
                articles.append({
                    'title': title,
                    'href': href,
                    'push_count': push_count
                })
    return articles


def get_download_list(img_urls, title, path='photos'):
    download_list = []
    dir_name = title.strip()
    dir_name = re.sub(r'[\\\/\:\*\?\"\<\>\|]', "", dir_name)
    dir_path = os.path.join(path, dir_name)
    try:
        os.makedirs(dir_path)
    except FileExistsError:
        pass
    except:
        print('makedirs failed')
        return None

    for img_url in img_urls:
        file_name = img_url.split('/')[-1]
        file_path = os.path.join(dir_path, file_name)
        if os.path.isfile(file_path) is False:
            download_list.append((img_url, file_path))

    return download_list


def save_urls(img_urls, title, path='photos'):
    pool = mp.Pool(8)
    download_list = []
    dir_name = title.strip()
    dir_name = re.sub(r'[\\\/\:\*\?\"\<\>\|]', "", dir_name)
    dir_path = os.path.join(path, dir_name)
    try:
        os.makedirs(dir_path)
    except FileExistsError:
        pass
    except:
        print('makedirs failed')
        return False

    for img_url in img_urls:
        file_name = img_url.split('/')[-1]
        file_path = os.path.join(dir_path, file_name)
        if os.path.isfile(file_path) is False:
            download_list.append((img_url, file_path))

    ret_jobs = [
        pool.apply_async(urllib.request.urlretrieve, args=(download[0], download[1],)) for download in download_list]
    ret = [j.get() for j in ret_jobs]

    return True


def get_photo_links(dom):
    soup = BeautifulSoup(dom, 'html.parser')

    photos = []  # 儲存取得的photo link
    # main_content = soup.find('main-content')
    push_content = soup.find('span', "f2")
    # extract 提出push 後的推文，soup就不包含了
    for elm in push_content.find_next_siblings():
        elm.extract()
    push_content.extract()
    divs = soup.find_all('div', 'richcontent')
    for d in divs:
        a = d.find('a')
        if a:
            photo_link = photo_init_url + a['href'].lstrip('/') + jpg_end
            photos.append(photo_link)

    return photos


def get_beauty(num, threshold=0, date=None):
    pool = mp.Pool()
    num_str = str(num)
    page = get_web_page(ptt_url + beauty_board_path + 'index' + num_str + '.html')

    if page:
        current_articles = get_articles(page, date)

        post_pages_jobs = [(post['title'], pool.apply_async(get_web_page, args=(ptt_url + post['href'],))) for post in
                           current_articles if post['push_count'] >= threshold]
        post_pages = [(j[0], j[1].get()) for j in post_pages_jobs]
        # print(post_pages)
        photo_links_jobs = [(post_page[0], pool.apply_async(get_photo_links, args=(post_page[1],))) for post_page in
                            post_pages]
        photo_links = [(j[0], j[1].get()) for j in photo_links_jobs]
        print(photo_links)
        download_lists = [get_download_list(photo_link[1], photo_link[0], os.path.join("photos", num_str)) for
                          photo_link in photo_links]
        download_list = []
        for this_list in download_lists:
            download_list.extend(this_list)

        ret_jobs = [
            pool.apply_async(urllib.request.urlretrieve, args=(download[0], download[1],)) for download in
            download_list]
        ret = [j.get() for j in ret_jobs]


        try:
            os.makedirs(os.path.join("photos", num_str))
        except FileExistsError:
            pass
        except:
            print('makedirs failed')
            return False
        json_path = os.path.join("photos", num_str, "data.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(current_articles, f, indent=2, sort_keys=True, ensure_ascii=False)
        return True
    return False




if __name__ == '__main__':

    parser = ArgumentParser()
    parser.add_argument("-r", "--range", help="index range", dest="index_range", default="0")
    parser.add_argument("-t", "--threshold", help="push threshold", dest="threshold", default="30")
    args = parser.parse_args()
    index_range = int(args.index_range) if int(args.index_range) > 0 else 0
    threshold = int(args.threshold)

    start_time = time.time()
    # sys.setrecursionlimit(20000)
    freeze_support()

    page = get_web_page(ptt_url + beauty_board)
    prev_page_link = get_prev_page_link(page)
    index_num = int(prev_page_link.split('/')[-1].split('.')[0].lstrip('index')) + 1
    for i in range(index_num - index_range, index_num):
        get_beauty(i, threshold)
    date = time.strftime("%m/%d").lstrip('0')
    get_beauty(index_num, threshold, date)


    end_time = time.time()
    elapsed = end_time - start_time
    print("Time taken: ", elapsed, "seconds.")
