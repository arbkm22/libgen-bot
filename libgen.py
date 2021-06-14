from bs4 import BeautifulSoup
from pathlib import Path
import requests, re, requests, os, sys

# Title filter, removes the ISBN no. from title
def titleFilter(title):
    title = title.split()
    while (len(title)>1):
        rf = re.findall(r"^[0-9,-]+[a-z]*$", string=title[-1], flags=re.IGNORECASE)
        if (len(rf) != 0):
            title.pop()
        else:
            break
    return " ".join(title)

# Download link grabber
def dlLinkGrabber(link):
    dlSource = requests.get(link)
    dlSoup = BeautifulSoup(dlSource.text, "lxml")
    dlSource = dlSoup.find("div", id="download")
    dlLink = dlSource.find("a")["href"]
    return dlLink

# Scraping site and collecting required info
def libgen(bookName):
    url = url = f'http://libgen.rs/search.php?req={bookName}&open=0&res=25&view=simple&phrase=1&column=def'
    source = requests.get(url)
    
    soup = BeautifulSoup(source.text, "lxml")
    table = soup.find("table", class_="c")
    tableRow = table.find_all("tr")
    pageList = []
    downloadLinksRef = []
    fileNameRef = []
    del tableRow[0]
    if (len(tableRow)>1):
        for tr in range(len(tableRow)):
            tableContent = tableRow[tr].find_all("td")
            bookId = tableContent[0].text
            title = tableContent[2].find("a", id=bookId).text
            title = titleFilter(title)
            fileNameRef.append(title)
            author = tableContent[1].text.strip()
            link = tableContent[9].find("a")["href"]
            downloadLinksRef.append(link)
            size = tableContent[7].text.strip()
            fileType = tableContent[8].text.strip()
            lang = tableContent[6].text.strip()
            data = {"title": title,
                    "author": author,
                    "lang": lang,
                    "size": size,
                    "ext": fileType,
                    "link": link}
            pageList.append(data)

    return pageList
