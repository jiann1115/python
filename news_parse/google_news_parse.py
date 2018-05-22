import jieba
import jieba.analyse
from argparse import ArgumentParser
from bs4 import BeautifulSoup
import requests
import re
from gensim import models, corpora
from lxml import html
import lxml
import ssl
import time
from lxml.html.clean import Cleaner
import os.path

sentence_t = '身為日本桌球名將同時身兼「台灣媳婦」的福原愛，去年生下寶貝女兒後吸金功力不減反增，一年收入上看1億元日幣，\
近日又與日本知名體育品牌簽下新的品牌大使合約，未來聲勢持續看漲。根據日媒報導，福原愛婚後已鮮少參加桌球賽事，專心經營家庭生活，\
然而她聲勢不減反增，代言更是接到手軟。尤其是她擔任的全日空形象大使，代言費用高達1.2億元日幣，其中還包括8千萬元日幣的合約費，\
荷包賺滿滿。此外，身為台灣好媳婦的福原愛幫夫運也超強。日前攜手老公江宏傑出席日本珠寶品牌代言記者會，兩人更一起合拍了家電廣告，\
如今福原愛又拿下日本運動品牌新合約，只能說一家人不只婚後幸福，荷包也進帳滿滿。（整理：實習編輯王世盈）'

sample_news_tuple = (
    '台灣女將郭婞淳在舉重58公斤級表現超狂 以抓舉107公斤 挺舉142公斤更破世界紀錄 以總和249公斤 收下我國本屆首面舉重金牌 \
同時也是生涯第二面世大運金牌 郭婞淳在2013年首度參加喀山世大運 以抓舉104公斤 挺舉134公斤 總和238公斤 3項全破世大運紀錄奪金；去年在\
里約奧運以231公斤摘銅 此次得面對來勢洶洶的里約奧運以總和240公斤摘金的泰國好手蘇甘雅 郭婞淳在享有地主觀眾龐大加油聲勢 抓舉開把重量為\
100公斤 挺舉為130公斤 皆為全場之冠 且當主要爭金勁敵蘇甘雅抓舉完成95公斤 她又改變戰術升至102公斤 逼得趕緊上陣的蘇甘雅挑戰100公斤\
失敗 第三次試舉才成功舉起 壓軸登場的郭婞淳第一把輕鬆抓起102公斤 第二次挑戰105公斤成功 改寫自己在2013年喀山世大運保持的104公斤 \
第三把又完成107公斤 以兩破大會紀錄 於抓舉暫居第一 當蘇甘雅以總和221公斤暫居第一 郭婞淳在挺舉仍舊是壓軸登場 且開把重量改成133公斤\
 她成功挺起 第二把又完成136公斤 直接改寫自己保持的134公斤大會紀錄 第三把再挺住142公斤重量 直接改寫141公斤世界紀錄',
    '中美貿易協商19日結束後 白宮發表中美聯合聲明 表示將 暫停 中美貿易戰 中國也將大幅增加對美國貨品與服務的採購 來縮減\
中國對美國的貿易逆差。然而這次的聲明具體承諾不多 對於智財權的保護尤其模糊 不確定性仍很高。甚至有分析指出 美國只是因為忙於北韓和中東問題\
暫時 停火 而不是 終戰')

def get_web_page_html(url):
    resp = requests.get(
        url=url,
        # allow_redirects=True
        cookies={'over18': '1'}

    )
    if resp.status_code != 200:
        print('Invalid url{0}:{1}'.format(resp.status_code, resp.url))
        # print(resp.text)
        return None
    else:
        return html.fromstring(resp.text)


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

#
# def analyse_keywords():
#     words_t = jieba.cut(sentence_t, cut_all=False)
#     key_num = {}
#     word_t_list = []
#     for word in words_t:
#         word_t_list.extend(word)
#         key_num[word] = key_num.get(word, 0) + 1
#
#     word_t_list = [word for word in words_t]
#     print(word_t_list)
#     jieba.analyse.set_stop_words("stop_words.txt")
#     tags = jieba.analyse.extract_tags(sentence_t, 5)
#     print(":".join(tags))
#     print(key_num)
#

def google_news_parse(dom):
    soup = BeautifulSoup(dom, 'html.parser')
    all_news = soup.find_all('a', 'nuEeue hzdq5d ME7ew')
    key_str = ""
    titles_link = []
    for news in all_news:
        # print(news.string)
        # print(news['href'])
        titles_link.append({'title': news.string, 'link': news['href']})
        key_str = key_str + news.string + "\n"

    jieba.load_userdict("my_dict.txt")
    jieba.load_userdict("news_dict.txt")
    jieba.analyse.set_stop_words("stop_words.txt")
    jieba.analyse.set_stop_words("stop_words_sport.txt")
    tags = jieba.analyse.extract_tags(key_str, 20)
    print("keywords: " + ", ".join(tags))
    documents = []
    for t_link in titles_link:
        page = get_web_page(t_link['link'])
        article_content = re.sub(u'[^\u4E00-\u9FA5]', " ", page)
        article_content = re.sub(r'[\n\xa0\W你妳我他她它們]', "", article_content)
        article_content = re.sub('自己', "", article_content)
        # for word in remove_words:
        #     article_content = re.sub(word, "", article_content)
        words_t = jieba.cut(article_content, cut_all=False)
        word_t_list = [word for word in words_t]
        documents.append(word_t_list)
    dictionary = corpora.Dictionary(documents)
    corpus = [dictionary.doc2bow(doc) for doc in documents]  # generate the corpus
    print(corpus)
    tf_idf = models.TfidfModel(corpus)  # the constructor

    # this may convert the docs into the TF-IDF space.
    # Here will convert all docs to TFIDF
    corpus_tfidf = tf_idf[corpus]

    # train the lsi model
    lsi_list = [models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=i) for i in range(2, 5)]
    for lsi in lsi_list:
        print('============================================================')
        topics = lsi.show_topics(num_words=20, log=0)
        for tpc in topics:
            print(tpc)

def google_news_cut(link):
    cleaner = Cleaner()
    cleaner.javascript = True  # This is True because we want to activate the javascript filter
    cleaner.style = True  # This is True because we want to activate the styles & stylesheet filter

    page = get_web_page(link)
    soup = BeautifulSoup(page, 'html.parser')
    # all_news = soup.find_all('a', 'nuEeue hzdq5d ME7ew')
    all_news = soup.find_all('a', 'ipQwMb Q7tWef')
    key_str = ""
    titles_link = []
    word_t_list = []
    documents = []
    for news in all_news:
        # print(news.string)
        # print(news['href'])
        if re.match('\./', news['href']) is None:
            link = news['href']
        else:
            link = 'https://news.google.com/' + re.sub('\./', "", news['href'])
        titles_link.append({'title': news.string, 'link': link})
        key_str = key_str + news.string + "\n"

    remove_words = ['mlb', 'nba', '新聞網', '中央社', '報紙', '聯合', '時報', '全網', '自己', '中時', '年月日',
                    '直播', '三立', '聞網', '使用者', '中國時報', '自由時報', '關鍵字', '網站', '發表', '留言', '發言',
                    '網小時', '自由']

    jieba.load_userdict("my_dict.txt")
    jieba.load_userdict("news_dict.txt")
    jieba.analyse.set_stop_words("stop_words.txt")
    jieba.analyse.set_stop_words("stop_words_sport.txt")

    for t_link in titles_link:

        print('get_web_page: ', t_link['title'], " ", t_link['link'])
        try:
            page = get_web_page_html(t_link['link'])
            # page = get_web_page(t_link['link'])
        except requests.exceptions.SSLError:
            continue
        except lxml.etree.ParserError:
            continue
        if page is None:
            continue
        cleaner.kill_tags = ['a', 'img']
        cleaner.remove_tags = ['div', 'p']
        cleaner.remove_unknown_tags = False
        cleaner.allow_tags = ['p']
        result = html.tostring(cleaner.clean_html(page), encoding="utf-8", pretty_print=True, method="html")
        article_content = re.sub('&#13;', "", result.decode('utf-8'))

        #
        article_content = re.sub(u'[^\u4E00-\u9FA5]', " ", article_content)
        article_content = re.sub(r'[\n\xa0\W你妳我他她它們]', "", article_content)
        article_content = re.sub('自己', "", article_content)
        # print(article_content)
        words_t = jieba.cut(article_content, cut_all=False)
        word_t_list = [word for word in words_t if word not in remove_words]
        print(word_t_list)
        documents.append(word_t_list)
    return documents

def make_lsi(lsi_file, documents):
    # 為每一個詞(word)分配一個id: {'一些': 0, '一年': 1, '一直': 2, '上': 3, ...}
    dictionary = corpora.Dictionary(documents)

    print("====== dictionary ==============================")
    print(dictionary)
    print(dictionary.token2id)

    # doc2bow計算每個唯一的詞(word)在此文出現的頻率:
    # [ [第1篇文], [第2篇文], ...]
    # [第1篇文] = [(詞id, 頻率), (),...]
    # [ [(0, 1), (1, 1),...], [(3, 1), (11, 2), (12, 4), ...], [], [] ]
    corpus = [dictionary.doc2bow(doc) for doc in documents]  # generate the corpus
    print('====== corpus:')
    print(corpus)
    tf_idf = models.TfidfModel(corpus)  # the constructor
    print('====== tf_idf:')
    print(tf_idf)
    # this may convert the docs into the TF-IDF space.
    # Here will convert all docs to TFIDF
    corpus_tfidf = tf_idf[corpus]
    print('====== corpus_tfidf:')
    print(corpus_tfidf)

    # train the lsi model (Latent Semantic Indexing, LSI)
    # lsi_list = [models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=i) for i in range(2, 6)]
    if os.path.isfile(lsi_file) is True:
        print('====== load ' + lsi_file)
        lsi = models.LsiModel.load(lsi_file)
        lsi.add_documents(corpus_tfidf)
    else:
        print('====== new ' + lsi_file)
        lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=10)

    lsi.save('model.lsi')
    return lsi

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("-t", "--threshold", help="push threshold", dest="threshold", default="30")
    args = parser.parse_args()
    threshold = int(args.threshold)
    # analyse_keywords()
    ssl._create_default_https_context = ssl._create_unverified_context

    start_time = time.time()

    news_links = ['https://news.google.com/gn/news/headlines/section/topic/WORLD.zh-TW_tw/國際?ned=tw',
                  'https://news.google.com/gn/news/headlines/section/topic/NATION.zh-TW_tw/台灣?ned=tw',
                  'https://news.google.com/gn/news/headlines/section/topic/BUSINESS.zh-TW_tw/財經?ned=tw',
                  'https://news.google.com/gn/news/headlines/section/topic/SCITECH.zh-TW_tw/科技?ned=tw',
                  'https://news.google.com/gn/news/headlines/section/topic/SPORTS.zh-TW_tw/體育?ned=tw',
                  'https://news.google.com/gn/news/headlines/section/topic/ENTERTAINMENT.zh-TW_tw/育樂?ned=tw',
                  'https://news.google.com/gn/news/headlines/section/topic/MAINLAND_CHINA.zh-TW_tw/兩岸?ned=tw',
                  'https://news.google.com/gn/news/headlines/section/topic/HEALTH.zh-TW_tw/健康?ned=tw']

    # google_news_parse(page)
    # for link in news_links:
    #     news_words = google_news_cut(link)
    #     documents.append(news_words)

    # new_documents = google_news_cut(news_links[0])
    # documents.extend(new_documents)
    # new_documents = google_news_cut(news_links[4])
    # documents.extend(new_documents)
    # new_documents = google_news_cut(news_links[5])
    # documents.extend(new_documents)
    # new_documents = google_news_cut(news_links[7])
    # documents.extend(new_documents)
    # new_documents = google_news_cut(news_links[1])
    # documents.extend(new_documents)
    # new_documents = google_news_cut(news_links[2])
    # documents.extend(new_documents)
    # new_documents = google_news_cut(news_links[3])
    # documents.extend(new_documents)
    # new_documents = google_news_cut(news_links[6])
    # documents.extend(new_documents)
    # print(documents)
    # lsi = make_lsi('model.lsi', documents)

    documents = []
    for news_link in news_links:
        documents = google_news_cut(news_link)
        lsi = make_lsi('model.lsi', documents)

    print('====== TOPIC ==============================')
    # lsi = models.LsiModel.load('model.lsi')
    topics = lsi.show_topics(num_words=20, log=0)
    for tpc in topics:
        print(tpc)
    for sample_news in sample_news_tuple:
        print('====== check sample_news')
        words_t = jieba.cut(sample_news, cut_all=False)
        word_t_list = [word for word in words_t]
        dictionary = corpora.Dictionary([word_t_list])
        sample_vec_bow = dictionary.doc2bow(word_t_list)
        print('====== sample_vec_bow:')
        print(word_t_list)
        print(sample_vec_bow)

        vec_lsi = lsi[sample_vec_bow]
        print('====== Correlation ==============================')
        print(vec_lsi)
        max = vec_lsi[0]
        for i in range(1, len(vec_lsi)):
            max = max if max[1] > vec_lsi[i][1] else vec_lsi[i]

        print('MAX: ' + str(max))

    print('====== END ==============================')
    end_time = time.time()
    elapsed = end_time - start_time
    print("Time taken: ", elapsed, "seconds.")
