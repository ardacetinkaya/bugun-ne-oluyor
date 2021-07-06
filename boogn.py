# pip install requests for installation
try:
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup

import sys
import getopt
from datetime import date
import jsons
import urllib
from urllib.error import HTTPError
from urllib.parse import quote
import os
from flask import Flask, render_template, request
import locale



class Entry:
    def __init__(self, title, url, postCount, date):
        self.title = title
        self.url = url
        self.postCount = postCount
        self.date = date
    def __str__(self) -> str:
        return self.title + " " + str(self.postCount)

class EntryContainer:
    def __init__(self,entries,date):
        self.entries = entries
        self.date = date

app = Flask(__name__)


@app.route('/')
def index():
    try:
        today = date.today()
        todayText = today.strftime("%d %B %Y").lstrip("0").replace(" 0", " ")
        months = {
            "January": "Ocak",
            "February": "Şubat",
            "March": "Mart",
            "April": "Nisan",
            "May": "Mayıs",
            "June": "HAziran",
            "July": "Temmuz",
            "August": "Ağustos",
            "September": "Eylül",
            "October": "Ekim",
            "November": "Kasım",
            "December": "Aralık"
            }
        searchQuery = todayText.replace(today.strftime("%B"),months[today.strftime("%B")])
        day = request.args.get('day', str(searchQuery))
        data = getEntries(day)
        container = EntryContainer(data,day)
        return render_template("index.html", data=jsons.dump(container))
    except Exception as ex:
        raise Exception(ex)


def getEntries(searchKeyword):
    try:
        print(f"Results for: {searchKeyword}")
        searchParameter = quote(searchKeyword)
        entries = []
        page = 1
        titles = []

        while True:
            url = f'https://eksisozluk.com/basliklar/ara?SearchForm.Keywords={searchParameter}&SearchForm.NiceOnly=false&SearchForm.FavoritedOnly=false&SearchForm.SortOrder=Date&p={str(page)}'
            request = urllib.request.Request(url,headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.64'})
            response = urllib.request.urlopen(request)
            htmlBytes = response.read()
            htmlStr = htmlBytes.decode("utf8")
            response.close()
            parsed_html = BeautifulSoup(htmlStr, "html5lib")
            titles = parsed_html.body.find('section', attrs={
                'id': 'content-body'}).find('ul', attrs={'class': 'topic-list'}).find_all()
            if len(titles) > 0:
                for title in titles:
                    if title.a != None:
                        if title.a.text.strip().startswith(searchKeyword.lower()):
                            titleText = title.a.text.replace(searchKeyword.lower(), "").replace(
                                "\n", "").replace("\r", "").strip()
                            entryURL = f"https://eksisozluk.com/{title.a['href']}"
                            entry = Entry(titleText, entryURL, 0, searchKeyword)
                            if title.a.small != None:
                                entry.title = entry.title.replace(
                                    str(title.a.small.text), "").strip()
                                if title.a.small.text.find("b") >= 0:
                                    entry.postCount = int(
                                        title.a.small.text[0])*1000
                                else:
                                    entry.postCount = int(title.a.small.text)

                            entry.title = entry.title.replace(
                                str(entry.postCount), "").strip()

                            if entry.title == "":
                                entry.title = searchKeyword.lower()
                            entries.append(entry)
            else:
                break

            page = page+1
        
        entries.sort(key=lambda x: x.postCount, reverse=True)
        sortedEntries  = sorted(entries, key=lambda x: x.postCount, reverse=True)
        return sortedEntries
    except HTTPError as err:
        print(f"{err}")
    except Exception as inst:
        print("something wrong")
        print(inst)
        print("Unexpected error:", sys.exc_info()[0])


def main(arguments):
    opts, args = getopt.getopt(arguments, 'd:h', ['date', 'help'])
    if len(opts) == 0:
        today = date.today()
        todayText = today.strftime("%d %B %Y").lstrip("0").replace(" 0", " ")
        months = {
            "January": "Ocak",
            "February": "Şubat",
            "March": "Mart",
            "April": "Nisan",
            "May": "Mayıs",
            "June": "HAziran",
            "July": "Temmuz",
            "August": "Ağustos",
            "September": "Eylül",
            "October": "Ekim",
            "November": "Kasım",
            "December": "Aralık"
            }
        searchQuery = todayText.replace(today.strftime("%B"),months[today.strftime("%B")])
        print(*getEntries(searchQuery), sep = "\n")
    else:
        for opt, arg in opts:
            if opt == '-h':
                print("boogn.py -d <date>")
                sys.exit()
            elif opt in ("-d", "--date"):
                print(*getEntries(arg), sep = "\n")

if __name__ == "__main__":
    locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')
    app.run()
    #main(sys.argv[1:])
