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
import shutil

lsi_file = 'model.lsi'
docs_file = 'docs.dict'
corpus_file = 'corpus.mm'


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

def load_stoplist(stopfile):
    stoplist = []
    changed = False
    try:
        with open(stopfile, "r") as f:
            for line in f:
                stoplist.append(line.strip())
    except Exception:
        return stoplist, changed

    stopfile_bak = stopfile + '.bak'
    changed = False if os.path.isfile(stopfile_bak) is True and \
                       os.path.getmtime(stopfile) == os.path.getmtime(stopfile_bak) else True
    if changed is True:
        shutil.copy2(stopfile, stopfile_bak)
    # print(os.path.getmtime(stopfile))
    # print(os.path.getmtime(stopfile_bak))

    return stoplist, changed

def dict_filter(dictionary, stoplist):
    stop_ids = [dictionary.token2id[stopword] for stopword in stoplist
                if stopword in dictionary.token2id]
    # once_ids = [tokenid for tokenid, docfreq in iteritems(dictionary.dfs) if docfreq == 1]
    # dictionary.filter_tokens(stop_ids + once_ids)  # remove stop words and words that appear only once
    dictionary.filter_tokens(stop_ids)  # remove stop words
    dictionary.compactify()  # remove gaps in id sequence after words that were removed

def make_dict_corpus(docs):
    # create/load dictionary from documents
    if os.path.isfile(docs_file) is True:
        dictionary = corpora.Dictionary.load(docs_file)
        dictionary.add_documents(docs)  # add more documents
        stoplist, changed = load_stoplist('stoplist.txt')
        if stoplist:
            dict_filter(dictionary, stoplist)
            corpus = [dictionary.doc2bow(doc) for doc in docs]  # generate the corpus
        else:
            corpus = list(corpora.MmCorpus(corpus_file))  # load the corpus mm file
            new_corpus = [dictionary.doc2bow(doc) for doc in docs]  # generate the new corpus
            corpus.extend(new_corpus)  # add new corpus
    else:
        dictionary = corpora.Dictionary(docs)
        stoplist, changed = load_stoplist('stoplist.txt')
        if stoplist:
            dict_filter(dictionary, stoplist)
        # Convert document into the bag-of-words (BoW) format = list of (token_id, token_count)
        corpus = [dictionary.doc2bow(doc) for doc in docs]  # generate the corpus

    dictionary.save(docs_file)
    corpora.MmCorpus.serialize(corpus_file, corpus)  # save to Matrix Market format
    return dictionary, corpus

def make_lsi(dictionary, corpus, num_topics=50):
    tf_idf = models.TfidfModel(corpus)  # the constructor, fit model
    # this may convert the docs into the TF-IDF space.
    # Here will convert all docs to TFIDF
    corpus_tfidf = tf_idf[corpus]
    lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=num_topics) # train model
    lsi.save(lsi_file)
    return lsi

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("-t", "--threshold", help="push threshold", dest="threshold", default="30")
    args = parser.parse_args()
    threshold = int(args.threshold)

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
    documents = []

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
    #
    for news_link in news_links:
        documents = google_news_cut(news_link)
        dictionary, corpus = make_dict_corpus(documents)

    lsi = make_lsi(dictionary, corpus)

    end_time = time.time()
    elapsed = end_time - start_time
    print("Time taken: ", elapsed, "seconds.")

    print('====== TOPIC ==============================')

    topics = lsi.show_topics(num_words=20, log=0)
    for tpc in topics:
        print(tpc)
