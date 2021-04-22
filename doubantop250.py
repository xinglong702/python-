# coding = utf-8

from bs4 import BeautifulSoup
import re
import urllib.request, urllib.error
import xlwt
import sqlite3
import datetime


def main():
    baseUrl = 'https://movie.douban.com/top250?start='
    savePath = '豆瓣电影Top250.xls'
    DBPath = 'Top250.db'
    dataList = getData(baseUrl)
    print('----------------------------------------------------------')
    saveDate(savePath, dataList)
    saveDateToDB(DBPath, dataList)


findLink = re.compile(r'<a class="" href="(.*?)">', re.S)
findImgSrc = re.compile(r'<img.*src="(.*?)\.jpg"', re.S)
findTitle = re.compile(r'<span class="title">(.*)</span>')
findRating = re.compile(r'average">(.*)</')
findJudge = re.compile(r'<span>(\d*)人评价</span>')
findInq = re.compile(r'<span class="inq">(.*)</span>')
findBd = re.compile(r'<p class="">(.*?)</p>', re.S)


def getData(baseUrl):
    dataList = []
    oldTime = datetime.datetime.now()
    for i in range(0, 10):
        print('爬取第%d页中，10页一共250条电影数据......' % (i + 1))
        url = baseUrl + str(i * 25)
        html = askUrl(url)
        soup = BeautifulSoup(html, 'html.parser')
        for item in soup.find_all('div', class_='item'):
            data = []
            item = str(item)
            link = re.findall(findLink, item)[0]
            data.append(link)
            imgSrc = re.findall(findImgSrc, item)[0]
            data.append(imgSrc + '.jpg')
            titles = re.findall(findTitle, item)
            if len(titles) == 2:
                cTitle = titles[0]
                data.append(cTitle)
                oTitle = titles[1].replace('/', '')
                data.append(oTitle)
            else:
                data.append(titles[0])
                data.append('null')
            rating = re.findall(findRating, item)[0]
            data.append(rating)
            judgeNum = re.findall(findJudge, item)[0]
            data.append(judgeNum)
            inq = re.findall(findInq, item)
            if len(inq) != 0:
                inq = inq[0].replace('。', '')
                data.append(inq)
            else:
                data.append('null')
            bd = re.findall(findBd, item)[0]
            bd = re.sub('<br(\s+)?/>(\s+)?', '', bd)
            bd = re.sub('/', '', bd)
            data.append(bd.strip())

            dataList.append(data)
    newTime = datetime.datetime.now()
    print('全部爬取完毕，总共用时%s秒' % (newTime - oldTime).seconds)
    return dataList


def askUrl(url):
    head = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0;Win64;x64) AppleWebKit/537.36(KHTML, likeGecko) Chrome/"
                      "90.0.4430.72Safari/537.36Edg/90.0.818.42 "
    }

    request = urllib.request.Request(url, headers=head)
    html = ''
    try:
        response = urllib.request.urlopen(request)
        html = response.read().decode('utf-8')
    except urllib.error.URLError as e:
        if hasattr(e, 'code'):
            print(e.code)
        if hasattr(e, 'reason'):
            print(e.reason)
    return html


def saveDate(savePath, dataList):
    print('开始写入excel......')
    book = xlwt.Workbook(encoding='utf-8', style_compression=0)
    sheet = book.add_sheet('豆瓣Top250', cell_overwrite_ok=True)
    col = ('电影详情链接', '图片链接', '影片中文名', '影片外国名', '评分', '评价人数', '概括', '相关信息')
    for i in range(0, 8):
        sheet.write(0, i, col[i])

    for i in range(1, 250):
        for j in range(0, 8):
            sheet.write(i, j, dataList[i - 1][j])

    book.save(savePath)
    print('写入完毕，excel文件在当前目录下！！！')
    print('----------------------------------------------------------')


def saveDateToDB(DBPath, dataList):
    print('开始写入数据库......')
    conn = sqlite3.connect(DBPath)
    print('成功打开数据库！！！')

    c = conn.cursor()
    sqlCreate = '''
        create table Top250
        (
            id integer primary key autoincrement,
            info_link text,
            pic_link text,
            cname varchar,
            ename varchar,
            score numeric ,
            rated numeric ,
            intro text,
            info text
        );
    '''
    c.execute(sqlCreate)
    conn.commit()

    for data in dataList:
        for idx in range(len(data)):
            data[idx] = '"' + data[idx] + '"'
        sqlInsert = '''
            insert into Top250 (
                info_link,pic_link,cname,ename,score,rated,intro,info
            )values(%s)''' % ",".join(data)
        c.execute(sqlInsert)
        conn.commit()

    print('成功建表!!!')
    conn.close()


if __name__ == '__main__':
    main()
