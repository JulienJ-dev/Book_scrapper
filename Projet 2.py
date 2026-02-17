import requests
import csv

from bs4 import BeautifulSoup

url = "https://books.toscrape.com/catalogue/the-mysterious-affair-at-styles-hercule-poirot-1_452/index.html"
product_infos = {}
books_infos_list = []

response = requests.get(url)
if response.ok:
    product_infos["url"] = url
    page_content = BeautifulSoup(response.text, "lxml")
    if page_content.find("li", class_="active").find_previous("a").get_text():
        product_infos["category"] = page_content.find("li", class_="active").find_previous("a").get_text()
    else:
        product_infos["category"] = None

    if page_content.find("article").find("h1") :
        product_infos["title"] = page_content.find("article").find("h1").get_text()
    else :
        product_infos["title"] = None
    if page_content.find("article").find("div", id="product_description"):
        product_infos["description"] = page_content.find("article").find("div", id="product_description").find_next("p").get_text()
    else:
        product_infos["description"] = "None"
    if page_content.find("article").find("img")["src"].replace("../..", "https://books.toscrape.com" ):
        product_infos["image url"] = page_content.find("article").find("img")["src"].replace("../..", "https://books.toscrape.com" )
    else : product_infos["image url"] = None
    if page_content.find("table") :
        table_info = page_content.find("table")
        for element in table_info.find_all("tr"):
            th = element.find("th")
            td = element.find("td")
            product_infos[th.get_text()] = td.get_text()
        product_infos["Price (excl. tax)"] = float(product_infos["Price (excl. tax)"].replace("Â£", ""))
        product_infos["Price (incl. tax)"] = float(product_infos["Price (incl. tax)"].replace("Â£", ""))
        product_infos["Availability"] = int(product_infos["Availability"].replace("In stock (", "").replace(" available)", ""))
        del product_infos["Number of reviews"]
        del product_infos["Tax"]
        del product_infos["Product Type"]
    else :
        product_infos["UPC", "Price (excl. tax)", "Price (incl. tax)", "Availability"] = None
    
    if page_content.find("div", class_="col-sm-6 product_main").find("p",class_="star-rating One") :
        product_infos["ranking"] = "1 sur 5"
    
    elif page_content.find("div", class_="col-sm-6 product_main").find("p",class_="star-rating Two") :
        product_infos["ranking"] = "2 sur 5"
    
    elif page_content.find("div", class_="col-sm-6 product_main").find("p",class_="star-rating Three") :
        product_infos["ranking"] = "3 sur 5"
    
    elif page_content.find("div", class_="col-sm-6 product_main").find("p",class_="star-rating Four") :
        product_infos["ranking"] = "4 sur 5"

    elif page_content.find("div", class_="col-sm-6 product_main").find("p",class_="star-rating Five") :
        product_infos["ranking"] = "5 sur 5"

    books_infos_list.append(product_infos)
    print (books_infos_list)
    print("\n--------------------------------------------\n")

    headers = books_infos_list[0].keys()

   
    with open ("book_info.csv", mode="w", newline="", encoding = "utf-8") as fichier:
        writer = csv.DictWriter(fichier, fieldnames=headers, delimiter=";")
        writer.writeheader()
        writer.writerows(books_infos_list)