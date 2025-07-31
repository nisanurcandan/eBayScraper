from flask import Flask, render_template, request
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import urllib.parse

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        keyword = request.form.get("keyword")
        if keyword:
            listings = get_ebay_results(keyword)
            return render_template("results.html", keyword=keyword, listings=listings)
    return render_template("search.html")

def get_ebay_results(keyword):
    encoded_keyword = urllib.parse.quote_plus(keyword)
    url = f"https://www.ebay.com/sch/i.html?_nkw={encoded_keyword}&_in_kw=2&_ex_kw=Beer&LH_TitleDesc=1&LH_Complete=1&LH_Sold=1&LH_SaleItems=1&_salic=216&LH_LocatedIn=1"

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)
    driver.implicitly_wait(5)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    listings = []
    ul = soup.find("ul", class_="srp-results srp-list clearfix")
    if not ul:
        return listings

    li_elements = ul.find_all("li", recursive=False)
    for li in li_elements:
        a_tag = li.find("a", href=True)
        img_tag = li.find("img")

        if not a_tag or not img_tag:
            continue

        title = img_tag.get("alt")
        href = a_tag.get("href")
        imageUrl = img_tag.get("src") or img_tag.get("data-defer-load")

        price = None
        location = None

        # Fiyat ve konum satırlarını tek tek ara
        rows = li.find_all("div", class_="s-card__attribute-row")
        for row in rows:
            span = row.find("span")
            if span:
                text = span.get_text(strip=True)
                if "$" in text and not price:
                    price = text
                elif "Located in" in text and not location:
                    location = text.replace("Located in", "").strip()

        listings.append({
            "title": title,
            "url": href,
            "imageUrl": imageUrl,
            "price": price or "Not found",
            "location": location or "Not found"
        })

    return listings

if __name__ == "__main__":
    app.run(debug=True)
