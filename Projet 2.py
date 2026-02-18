import requests
import csv

from bs4 import BeautifulSoup

def export_csv(csv_name, list_to_implement):

    headers = list_to_implement[0].keys()
    with open (csv_name, mode="w", newline="", encoding = "utf-8") as fichier:
        writer = csv.DictWriter(fichier, fieldnames=headers, delimiter=";")
        writer.writeheader()
        writer.writerows(list_to_implement)

def grab_pages_urls(base_url, page_content):

    pages_urls = []

    if page_content.find("div", class_ = "col-sm-8 col-md-9").find("li", class_ = "current"):
        page_quantity = page_content.find("div", class_ = "col-sm-8 col-md-9").find("li", class_ = "current").get_text(strip=True).replace("Page 1 of ", "")

        for i in range (0, int(page_quantity)) :
            pages_urls.append(base_url.replace("index", "page-"+ str(i+1)))
        return pages_urls

    else :
        pages_urls.append(base_url)
        return pages_urls

def collect_urls_products(pages_urls) :

    #Cette fonction utilise en paramètre la liste des urls contenant toutes les pages du catalogue
    #Une boucle for cherche récupère dans chaque page le code html, tandis qu'une autre boucle for imbriquée récupère le lien de chaque article de chaque page, le stocke dans urls_products et renvoie la liste

    urls_products = []
    for url in pages_urls :
        response = requests.get(url)
        page_content = BeautifulSoup(response.text, "lxml")
        product_info = page_content.select("article")
        for article in product_info :
            a = article.find('a')
            urls_products.append("https://books.toscrape.com/catalogue/" + a["href"].replace("../../../", ""))
    return urls_products

def scrapping_infos_per_category(products_urls):
     
    category_infos_list = []
    for url in products_urls:
        product_infos = {}
        print(f"scrapping en cours sur {url}")
        response = requests.get(url)
        if response.ok:
            product_infos["url"] = url
            product_page_content = BeautifulSoup(response.text, "lxml")
            if product_page_content.find("li", class_="active").find_previous("a").get_text():
                product_infos["category"] = product_page_content.find("li", class_="active").find_previous("a").get_text()
            else:
                product_infos["category"] = None

            if product_page_content.find("article").find("h1") :
                product_infos["title"] = product_page_content.find("article").find("h1").get_text()
            else :
                product_infos["title"] = None
            if product_page_content.find("article").find("div", id="product_description"):
                product_infos["description"] = product_page_content.find("article").find("div", id="product_description").find_next("p").get_text()
            else:
                product_infos["description"] = "None"
            if product_page_content.find("article").find("img")["src"].replace("../..", "https://books.toscrape.com" ):
                product_infos["image url"] = product_page_content.find("article").find("img")["src"].replace("../..", "https://books.toscrape.com" )
            else : product_infos["image url"] = None
            if product_page_content.find("table") :
                table_info = product_page_content.find("table")
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
            
            if product_page_content.find("div", class_="col-sm-6 product_main").find("p",class_="star-rating One") :
                product_infos["ranking"] = "1 sur 5"
            
            elif product_page_content.find("div", class_="col-sm-6 product_main").find("p",class_="star-rating Two") :
                product_infos["ranking"] = "2 sur 5"
            
            elif product_page_content.find("div", class_="col-sm-6 product_main").find("p",class_="star-rating Three") :
                product_infos["ranking"] = "3 sur 5"
            
            elif product_page_content.find("div", class_="col-sm-6 product_main").find("p",class_="star-rating Four") :
                product_infos["ranking"] = "4 sur 5"

            elif product_page_content.find("div", class_="col-sm-6 product_main").find("p",class_="star-rating Five") :
                product_infos["ranking"] = "5 sur 5"

            category_infos_list.append(product_infos)
    return category_infos_list

url = "https://books.toscrape.com"

response = requests.get(url)
if response.ok:

    
    page_content = BeautifulSoup(response.text, "lxml")
    if page_content.find("form", method="get", class_="form-horizontal"):
        books_quantity = page_content.find("form", method="get", class_="form-horizontal").find_next("strong").get_text(strip=True)
    if page_content.find("ul", class_="nav nav-list").find_next("ul").find("li"):
        for element in page_content.find("ul", class_="nav nav-list").find_next("ul").find_all("li"):
            pages_urls=[]
            new_category_url = (url + "/" + element.find("a")["href"])
            category_name = (element.find("a").get_text(strip = True))
            print("\nCategory " + category_name + "\n")
            category_page_response = requests.get(new_category_url)
            if category_page_response.ok:
                category_page_content = BeautifulSoup(category_page_response.text, "lxml")
                pages_urls.extend(grab_pages_urls(new_category_url,category_page_content))
                products_urls = collect_urls_products(pages_urls)
                books_infos_per_category = scrapping_infos_per_category(products_urls)
                export_csv(category_name +".csv", books_infos_per_category)
                print("\n"+ category_name +".csv succesfully updated\n")
    else:
        print("Error during searching categories' urls")
        exit

    
    print("Scrapping ended, CSV updated")