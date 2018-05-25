import jieba
import jieba.analyse
from gensim import models, corpora
import matplotlib.pyplot as plt


lsi_file = 'model.lsi'
docs_file = 'docs.dict'

sample_news_tuple = (
    '面對打擊率3成保衛戰，大谷翔平用單場3打數2安打、2保送的表現，再度將打擊率提升到3成19，加上楚奧特（Mike Trout）、\
    普荷斯（Albert Pujols）的陽春砲，捕手馬多納度（Martin Maldonado）貢獻3打點，天使以8：1擊敗藍鳥拿下2連勝。\
    在天使出賽超過10場的球員中，大谷翔平的打擊率僅低於西門斯（Andrelton Simmons）的3成31，而且只要大谷單場站上壘包2次以上\
    ，天使的戰績是11勝2敗，幾乎是贏球保證，而大谷今天2安打、2保送，則是生涯第一次單場複數安打加複數保送',

    '美國總統川普（Donald Trump）24日正式取消美國、北韓領導人會議（簡稱川金會）後，北韓《朝中社》25日早晨7點多的最新回應報導指出\
    ，北韓願意隨時與美國展開會談；北韓領導人金正恩仍全力以赴準備與川普會面。朝中社 引述北韓外務省第一副相金桂冠發出的聲明報導，\
    美國單方面取消美國、北韓領導人會議，顯示兩國之間存有嚴重敵意，因此兩國領導人召開高峰會是很必要的',

    '一名17歲高中生只要進食就會吐，就醫確診竟是胃癌第四期。醫師表示，胃癌多為非特定性症狀，經常和其他腸胃疾病搞混，不易早期發現，\
    台灣胃癌患者確診多已中晚期，建議少吃醃漬食品、避免菸酒，並定期健康檢查，當腸胃道不適症狀持續2週以上，就要提高警覺，\
    並提醒少吃醃漬食品、避免菸酒，以及定期健康檢查',

    '余祥銓爆出憂鬱症復發，住進榮總觀察，雖然如今已出院，但昨《歌神請上車》節目工作人員爆料，余祥銓在遊戲關卡時突然失控，當集來賓\
    「后的男人」錦榮遭殃，余祥銓對著他揮拳，「時間很久，大家都覺得不太對')

if __name__ == '__main__':
    dictionary = corpora.Dictionary.load(docs_file)
    lsi = models.LsiModel.load(lsi_file)
    print('====== TOPIC ==============================')

    topics = lsi.show_topics(num_words=20, log=0)
    for tpc in topics:
        print(tpc)

    jieba.load_userdict("my_dict.txt")
    jieba.load_userdict("news_dict.txt")
    jieba.analyse.set_stop_words("stop_words.txt")
    jieba.analyse.set_stop_words("stop_words_sport.txt")
    for sample_news in sample_news_tuple:
        print('====== check sample_news')
        words_t = jieba.cut(sample_news, cut_all=False)
        word_t_list = [word for word in words_t]
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
        plt.bar([vec[0] for vec in vec_lsi], [vec[1] for vec in vec_lsi])
        plt.ylabel('Correlation')
        plt.show()

    print('====== END ==============================')
