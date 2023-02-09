from flask import Flask, render_template
from bs4 import BeautifulSoup
from datetime import *
import requests
import re

app = Flask(__name__)

def get_latest_news():
    ## TECHRADAR ##

    # Get techradar news page
    page = requests.get("https://www.techradar.com/uk/news")
    soup = BeautifulSoup(page.content, "html.parser")

    # Get article name, synopsis from techradar
    latest_news_title = soup.find_all("h3", class_="article-name")
    latest_news_synop = soup.find_all("p", class_="synopsis")
    
    latest_news_link = []

    # For each link, get aria-label and href attributes value
    for item in soup.find_all("a", class_="article-link"):
        if item.has_attr("aria-label") and item.has_attr("href"):
            latest_news_link.append({
                "label": item["aria-label"],
                "link": item["href"]
            })
    
    latest_news = []

    # For each article name, add a dictionary with the title of news article and which site its from
    for i in range(0, len(latest_news_title)):
        latest_news.append({
            "title": latest_news_title[i].text,
            "publisher": "TechRadar"
        })
    
    # For each article synopsis, add a synopsis key to the dictionary
    for i in range(0, len(latest_news_synop)):
        latest_news[i]["synop"] = latest_news_synop[i].text
    

    # Add link for each article to latest_news
    count = 0

    for i in range(0, len(latest_news_link)):
        if latest_news_link[i]["label"] == latest_news[count]["title"]:
            latest_news[count]["link"] = latest_news_link[i]["link"]
            count += 1
        
        if count == len(latest_news):
            break
    
    # Get time articles were posted
    latest_time = soup.find_all("time")

    # Add time posted to latest_news
    for i in range(0, len(latest_news)):
        posted_time = latest_time[i]["datetime"].split("T")

        date = posted_time[0].split("-")
        time = re.split(":|Z", posted_time[1])

        latest_news[i]["year"] = date[0]
        latest_news[i]["month"] = date[1]
        latest_news[i]["day"] = date[2]
        latest_news[i]["hour"] = time[0]
        latest_news[i]["minute"] = time[1]

        latest_news[i]["dt"] = datetime(
            year=int(latest_news[i]["year"]),
            month=int(latest_news[i]["month"]),
            day=int(latest_news[i]["day"]),
            hour=int(latest_news[i]["hour"]),
            minute=int(latest_news[i]["minute"])
        )
    

    ## TECHCRUNCH ##
    page = requests.get("https://techcrunch.com/")
    soup = BeautifulSoup(page.content, "html.parser")

    crunch_latest_news = []

    # Get title, link from techcrunch latest articles
    for item in soup.find_all("a", class_="post-block__title__link"):
        if item.has_attr("href"):
            crunch_latest_news.append({
                "title": item.text,
                "link": item["href"],
                "publisher": "TechCrunch"
            })

    # Get synopsis
    crunch_latest_synop = soup.find_all("div", class_="post-block__content")

    # Add synopsis to crunch latest news
    for i in range(0, len(crunch_latest_synop)):
        crunch_latest_news[i]["synop"] = crunch_latest_synop[i].text

    # Get time posted
    crunch_latest_time = soup.find_all("time")

    # Add time posted to crunch_latest_news
    for i in range(0, len(crunch_latest_time)):
        posted_time = crunch_latest_time[i]["datetime"].split("T")


        date = posted_time[0].split("-")
        time = re.split(":|-", posted_time[1])
        
        crunch_latest_news[i]["year"] = date[0]
        crunch_latest_news[i]["month"] = date[1]
        crunch_latest_news[i]["day"] = date[2]
        crunch_latest_news[i]["hour"] = time[0]
        crunch_latest_news[i]["minute"] = time[1]
        
        crunch_latest_news[i]["dt"] = datetime(
            year=int(crunch_latest_news[i]["year"]),
            month=int(crunch_latest_news[i]["month"]),
            day=int(crunch_latest_news[i]["day"]),
            hour=int(crunch_latest_news[i]["hour"]),
            minute=int(crunch_latest_news[i]["minute"])
        )

    # Append crunch_latest_news items to latest_news
    for i in crunch_latest_news:
        latest_news.append(i)

    # Remove latest news without date and append to no_date, if title is not included/is whitespace remove completely
    no_date = []
    count = 0

    while count < len(latest_news):
        if "title" not in latest_news[count] or latest_news[count]["title"].isspace():
            latest_news.pop(count)
        elif "dt" not in latest_news[count]:
            no_date.append(latest_news.pop(count))
        else:
            count += 1
        
    # Sort latest_news by date
    latest_news.sort(key = lambda x:x["dt"])

    # Add news with no date back to the end of latest_news
    for i in no_date:
        latest_news.append(i)

    
    return latest_news


@app.route("/")
def index():
    latest_news = get_latest_news()
    return render_template("news_index.html", latest_news=latest_news)

@app.route("/sort/newest")
def sort_newest():
    # Sort latest_news by newest date (default)
    latest_news = get_latest_news()
    return render_template("news_index.html", latest_news=latest_news)

@app.route("/sort/title")
def sort_title():
    # Sort latest_news by title in ascending order
    latest_news = sorted(get_latest_news(), key=lambda x: x["title"])
    return render_template("news_index.html", latest_news=latest_news)  

@app.route("/sort/publisher")
def sort_publisher():
    # Sort latest_news by publisher in ascending order
    latest_news = sorted(get_latest_news(), key=lambda x: x["publisher"])
    return render_template("news_index.html", latest_news=latest_news) 

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80)