import jieba
import jieba.analyse
from argparse import ArgumentParser
from bs4 import BeautifulSoup
import requests
import re
from gensim import models,corpora

sentence_t = '身為日本桌球名將同時身兼「台灣媳婦」的福原愛，去年生下寶貝女兒後吸金功力不減反增，一年收入上看1億元日幣，近日又與日本知名體育品牌簽下新的品牌大使合約，未來聲勢持續看漲。'
sentence_t = sentence_t + '根據日媒報導，福原愛婚後已鮮少參加桌球賽事，專心經營家庭生活，然而她聲勢不減反增，代言更是接到手軟。尤其是她擔任的全日空形象大使，代言費用高達1.2億元日幣，其中還包括8千萬元日幣的合約費，荷包賺滿滿。'
sentence_t = sentence_t + '此外，身為台灣好媳婦的福原愛幫夫運也超強。日前攜手老公江宏傑出席日本珠寶品牌代言記者會，兩人更一起合拍了家電廣告，如今福原愛又拿下日本運動品牌新合約，只能說一家人不只婚後幸福，荷包也進帳滿滿。（整理：實習編輯王世盈）'

this_link = 'https://www.cw.com.tw/article/article.action?id=5089814'
news_links = ['https://www.cw.com.tw/article/article.action?id=5089814',
              'https://www.cw.com.tw/article/article.action?id=5089773',
              'https://www.cw.com.tw/article/article.action?id=5089832']
channels = {'產業':'https://www.cw.com.tw/masterChannel.action?idMasterChannel=7',
            '財經':'https://www.cw.com.tw/masterChannel.action?idMasterChannel=8',
            '國際':'https://www.cw.com.tw/masterChannel.action?idMasterChannel=9',
            '管理':'https://www.cw.com.tw/masterChannel.action?idMasterChannel=10',
            '生活':'https://www.cw.com.tw/masterChannel.action?idMasterChannel=11',
            '環境':'https://www.cw.com.tw/masterChannel.action?idMasterChannel=12',
            '教育':'https://www.cw.com.tw/masterChannel.action?idMasterChannel=13',
            '政治':'https://www.cw.com.tw/masterChannel.action?idMasterChannel=77',
            '健康':'https://www.cw.com.tw/masterChannel.action?idMasterChannel=79'}
cw_today = 'https://www.cw.com.tw/today'

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


def get_today_topic(dom):
    soup = BeautifulSoup(dom, 'html.parser')
    subArticles = soup.find_all('section', 'subArticle')

    links = [caption.find('a')['href'] for caption in subArticles]
    return links


def get_channel_topic(dom):
    links = []
    soup = BeautifulSoup(dom, 'html.parser')
    article_grp = soup.find_all('div', 'articleGroup')
    # print(article_grp)
    for article in article_grp:
        articles = article.find_all('div', 'pic')
        # print(articles)
        for caption in articles:
            links.append(caption.find('a')['href'])
    return links

def get_articles(dom):
    soup = BeautifulSoup(dom, 'html.parser')
    keyword_section = soup.find('section', 'keyword list-inline')
    keyword_all_a = keyword_section.find_all('a')
    keywords = [key_word.string for key_word in keyword_all_a]
    article = soup.find('section', 'nevin')
    scripts = soup.find_all('script')
    for s in scripts:
        s.extract()
    links = soup.find_all('a')
    for s in links:
        s.extract()
    title = article.find('h2').string
    content = article.get_text()
    return {'title': title, 'content': content, 'keyword': keywords}

def news_cut(link):
    page = get_web_page(link)
    article = get_articles(page)
    # jieba.load_userdict("my_dict.txt")
    # jieba.load_userdict("news_dict.txt")
    # jieba.analyse.set_stop_words("stop_words.txt")
    # 刪除多餘字串
    article_content = re.sub(r'[\n\xa0\W你妳我他她它們]', "", article['content'])
    article_content = re.sub('自己', "", article_content)
    # article_content = re.sub('(\u3000)|(\x00)|(nbsp)', '', article_content)
    print(article['title'])

    words_t = jieba.cut(article_content, cut_all=False)

    word_t_list = [word for word in words_t]
    # print(word_t_list)
    return word_t_list

def news_tags_parse(link, topK=10):
    page = get_web_page(news_link)
    article = get_articles(page)
    # print(page)
    print(article['title'])
    # print(article['content'])
    print(article['keyword'])
    jieba.load_userdict("my_dict.txt")
    jieba.load_userdict("news_dict.txt")
    jieba.analyse.set_stop_words("stop_words.txt")
    tags = jieba.analyse.extract_tags(article['content'], topK)
    return tags

def test_jieba():
    words_t = jieba.cut(sentence_t, cut_all=False)
    key_num = {}
    word_t_list = []
    for word in words_t:
        word_t_list.extend(word)
        key_num[word] = key_num.get(word, 0) + 1

    word_t_list = [word for word in words_t]
    print(word_t_list)
    jieba.analyse.set_stop_words("stop_words.txt")
    tags = jieba.analyse.extract_tags(sentence_t, 5)
    print(":".join(tags))
    print(key_num)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("-t", "--threshold", help="push threshold", dest="threshold", default="30")
    args = parser.parse_args()
    threshold = int(args.threshold)
    # test_jieba()

    documents = []
    channel_links = {}
    for key, value in channels.items():
        # print(key)
        page = get_web_page(value)
        topics = get_channel_topic(page)
        # print(topics)
        channel_links[key] = topics
    topic_keys = ['環境', '健康', '生活', '管理', '國際']
    for key in topic_keys:
        print('*TOPIC: ' + key)
        for news_link in channel_links[key]:
            news_words = news_cut(news_link)
            documents.append(news_words)


    dictionary = corpora.Dictionary(documents)
    corpus = [dictionary.doc2bow(doc) for doc in documents]  # generate the corpus
    tf_idf = models.TfidfModel(corpus)  # the constructor

    # this may convert the docs into the TF-IDF space.
    # Here will convert all docs to TFIDF
    corpus_tfidf = tf_idf[corpus]

    # train the lsi model
    lsi_list = [models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=i) for i in range(2,5)]

    for lsi in lsi_list:
        print('*************************************')
        topics = lsi.show_topics(num_words=20, log=0)
        for tpc in topics:
            print(tpc)

    # channel_links = {}
    # for key, value in channels.items():
    #     # print(key)
    #     page = get_web_page(value)
    #     topics = get_channel_topic(page)
    #     # print(topics)
    #     channel_links[key] = topics
    # print(channel_links)


    # today = get_web_page(cw_today)
    # topics = get_today_topic(today)
    # print(topics)


    # for news_link in topics:
    #     tags = news_tags_parse(news_link)
    #     print("keywords: " + ", ".join(tags))
