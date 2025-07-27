from flask import Flask, render_template, request
from bs4 import BeautifulSoup
import httpx
import urllib.parse

app = Flask("__name__")

@app.route("/", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        keyword = request.form.get("keyword")
        if keyword:
            return render_template("results.html", listings=get_ebay_results(keyword), keyword=keyword)
    return render_template("search.html")

def get_ebay_results(keyword):
    encoded_keyword = urllib.parse.quote_plus(keyword)
    
    url = (
        f"https://www.ebay.com/sch/i.html?_nkw={encoded_keyword}&_in_kw=2&_ex_kw=Beer&LH_TitleDesc=1&LH_Complete=1&LH_Sold=1&LH_SaleItems=1&_salic=216&LH_LocatedIn=1"
    )


    listings = []

    try:
        response = httpx.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        ul = soup.find("ul", class_="srp-results srp-list clearfix")

        if ul:
            li_elements = ul.find_all("li", recursive=False)
            for li in li_elements:
                a_tag = li.find("a")
                if a_tag:
                    title = a_tag.find("img").get("alt")
                    href = a_tag.get("href")
                    imageUrl = a_tag.find("img").get("data-defer-load")
                    listings.append({"title": title, "url": href, "imageUrl": imageUrl})

    except Exception as e:
        print("Scraping error:", e)

    return listings

if __name__ == "__main__":
    app.run(debug=True)