# get PTT beauty photos


利用requests和BeautifulSoup去抓取[ptt表特版](www.ptt.cc/bbs/Beauty/index.html)的照片

使用指令如下:

    get_beauty_mp.py : multiprocessing
    get_beauty_asyncio.py : asyncio


    usage: get_beauty_mp.py [-h] [-r INDEX_RANGE] [-t THRESHOLD]
    usage: get_beauty_asyncio.py [-h] [-r INDEX_RANGE] [-t THRESHOLD]


    optional arguments:
      -h, --help            show this help message and exit
      -r INDEX_RANGE, --range INDEX_RANGE
                            index range
      -t THRESHOLD, --threshold THRESHOLD
                            push threshold


使用multiprocessing和asyncio去同步抓取每一篇文的照片
在這個範本之中，測試的時間看起來multiprocessing比較有效率

    python get_beauty_mp.py -r 5 -t 30
    ...省略
    Time taken:  66.02977681159973 seconds.

    python get_beauty_asyncio.py -r 5 -t 30
    ...省略
    Time taken:  100.18873023986816 seconds.

每篇文章的照片會放入不同的資料夾:

![image](https://github.com/jiann1115/python/blob/master/beauty_get/beauty_folder.png)
