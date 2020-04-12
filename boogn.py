# pip install requests for installation
try:
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup

import sys
import getopt
import jsons
import urllib
from urllib.parse import quote
import os
from flask import Flask, render_template, request


class Entry:
    def __init__(self, title, url, postCount, date):
        self.title = title
        self.url = url
        self.postCount = postCount
        self.date = date

class EntryContainer:
    def __init__(self,entries,date):
        self.entries = entries
        self.date = date

app = Flask(__name__)


@app.route('/')
def index():
    try:
        day = request.args.get('day', '12 Nisan 2020')
        data = getEntries(day)
        container = EntryContainer(data,day);
        return render_template("index.html", data=jsons.dump(container))
    except:
        return render_template("index.html", data=None)


def getEntries(searchKeyword):
    try:
        print(f"Results for: {searchKeyword}")
        searchParameter = quote(searchKeyword)
        entries = []
        page = 1
        titles = []

        while True:
            url = f'https://eksisozluk.com/basliklar/ara?SearchForm.Keywords={searchParameter}&SearchForm.NiceOnly=false&SearchForm.FavoritedOnly=false&SearchForm.SortOrder=Date&p={str(page)}'
            request = urllib.request.Request(url)
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

        for entry in entries:
            print(f"{entry.title}-{entry.postCount}")

        return entries

    except Exception as inst:
        print("something wrong")
        print(inst)
        print("Unexpected error:", sys.exc_info()[0])


def main(arguments):
    try:
        opts, args = getopt.getopt(arguments, 'd:h', ['date', 'help'])
    except:
        print("Check command arguments")
        print("boogn.py -d <date>")
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print("boogn.py -d <date>")
            sys.exit()
        elif opt in ("-d", "--date"):
            getEntries(arg)


if __name__ == "__main__":
    app.run()
    # main(sys.argv[1:])
