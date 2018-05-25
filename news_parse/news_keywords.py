import jieba
import jieba.analyse

sentence_t = '身為日本桌球名將同時身兼「台灣媳婦」的福原愛，去年生下寶貝女兒後吸金功力不減反增，一年收入上看1億元日幣，\
近日又與日本知名體育品牌簽下新的品牌大使合約，未來聲勢持續看漲。根據日媒報導，福原愛婚後已鮮少參加桌球賽事，專心經營家庭生活，\
然而她聲勢不減反增，代言更是接到手軟。尤其是她擔任的全日空形象大使，代言費用高達1.2億元日幣，其中還包括8千萬元日幣的合約費，\
荷包賺滿滿。此外，身為台灣好媳婦的福原愛幫夫運也超強。日前攜手老公江宏傑出席日本珠寶品牌代言記者會，兩人更一起合拍了家電廣告，\
如今福原愛又拿下日本運動品牌新合約，只能說一家人不只婚後幸福，荷包也進帳滿滿。（整理：實習編輯王世盈）'

def analyse_keywords():
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
    analyse_keywords()