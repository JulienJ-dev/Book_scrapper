import requests
import csv
from pathlib import Path
from bs4 import BeautifulSoup

def check_category_pages_quantity(base_url, page_content): # Paramètres : l'url de la page et son contenu. Vérifie le nombre de pages pour chaque categorie et renvoie la liste des urls de chaque page
    pages_urls = []
    if page_content.find("div", class_ = "col-sm-8 col-md-9").find("li", class_ = "current"): # La fonction teste la présence de la balise li class = "current" contenant la chaine de caractères du bas de page "Page 1 of ..."
        page_quantity = page_content.find("div", class_ = "col-sm-8 col-md-9").find("li", class_ = "current").get_text(strip=True).replace("Page 1 of ", "") # Le texte est récupéré et supprimé, sauf le dernier chiffre, indiquant le nombre total de page dans la catégorie ciblée
        for i in range (0, int(page_quantity)) :
            pages_urls.append(base_url.replace("index", "page-"+ str(i+1))) # modification des urls par une boucle for pour y intégrer les numéros de pages
        return pages_urls
    else :
        pages_urls.append(base_url)
        return pages_urls    # La fonction retourne un tableau contenant toutes les urls des pages de la categorie grâce à la boucle for
    
def collect_urls_products(pages_urls) : # Paramètre : la liste des urls des pages à scrapper. Récupére toutes les urls de chaque article de la catégorie et les retourne dans une liste
    urls_products = []
    for url in pages_urls :     #Une boucle for cherche et récupère dans chaque page le code html
        response = requests.get(url)
        page_content = BeautifulSoup(response.content, "lxml")
        product_info = page_content.select("article")
        for article in product_info :  # tandis qu'une autre boucle for imbriquée récupère le lien de chaque article de chaque page proprement, le stocke dans urls_products et renvoie la liste
            a = article.find('a')
            urls_products.append("https://books.toscrape.com/catalogue/" + a["href"].replace("../../../", ""))
    return urls_products

def scrapping_infos_per_category(products_urls, category_name):     # Paramètres : le tableau des urls de chaque article et le nom de la catégorie. Récupère toutes les données ciblées de chaque article
    i = 0
    category_infos_list = []
    for url in products_urls:     # Une boucle for permet de passer sur chaque url présente dans la liste products_urls pour en récupérer le contenu et ajouter au dict product_infos, toutes les données ciblées
        i+= 1
        progress = round(i / len(products_urls) * 100)
        product_infos = {}
        print(f"Scrapping progress for the {category_name} category : {progress} %")
        #print(f"scrapping in progress on {url}")
        response = requests.get(url)
        if response.ok:
            product_infos["url"] = url
            product_page_content = BeautifulSoup(response.content, "lxml")
            if product_page_content.find("li", class_="active").find_previous("a").get_text():
                product_infos["category"] = product_page_content.find("li", class_="active").find_previous("a").get_text()
            else:
                product_infos["category"] = None
            if product_page_content.find("article").find("h1") :
                product_infos["title"] = product_page_content.find("article").find("h1").get_text()
            else :
                product_infos["title"] = None
            if len(product_infos["title"]) > 50:
                product_infos["title"] = product_infos["title"][:50] + "..."
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
                product_infos["Price (excl. tax)"] = float(product_infos["Price (excl. tax)"].replace("£", ""))
                product_infos["Price (incl. tax)"] = float(product_infos["Price (incl. tax)"].replace("£", ""))
                product_infos["Availability"] = int(product_infos["Availability"].replace("In stock (", "").replace(" available)", ""))
                del product_infos["Number of reviews"]     # Les données récupérées en trop en récupérant toutes les cellules td sont supprimées
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

            category_infos_list.append(product_infos)    # Le dict est ensuite ajouté à la liste category_infos_list qui est retournée
    return category_infos_list

def download_book_image(category_products_infos, category_name, base_dir): # Paramètres : la liste des infos des livres de la catégorie, le nom de la catégorie et le chemin du fichier racine. Télécharge les images de chaque article et les ajoute dans un dossier spécifique par catégorie.
    i = 0 # compteur pour indication de l'avancée des téléchargements
    FOLDER = base_dir / "Books_visuals"
    CHILD_FOLDER = FOLDER / category_name
    FOLDER.mkdir(parents=True, exist_ok = True)
    CHILD_FOLDER.mkdir(parents=True, exist_ok = True)
    print( category_name + " books visuals download in progress")
    for element in category_products_infos:
        i += 1
        print("downloading " + str(i) + " on " + str(len(category_products_infos)) + " images")
        title = element["title"]
        for char in r'\/:*?"<>|':
            title = title.replace(char, "-")
        url_image = element["image url"]
        filepath = CHILD_FOLDER / f"{title}.jpg"
        response = requests.get(url_image)
        if response.ok:
            with filepath.open (mode="wb") as f:
                f.write(response.content)
    
    return
    
def export_csv(csv_name, list_to_implement, base_dir):     # Cette fonction prend en paramètres le nom du csv à ouvrir/créer, et la liste des données à y implanter, elle crée un dossier dans lequel elle créera les csv contenant les données des articles de chaque catégorie
    FOLDER = base_dir / "Books_toscrape_datas"
    FOLDER.mkdir(parents=True, exist_ok=True) # Création d'un dossier pour contenir les csv et ainsi éviter la sauvegarde à la racine
    filepath = FOLDER / csv_name
    headers = list_to_implement[0].keys()     # La liste des headers est générée en récupérant toutes les clés du dictionnaire présent dans la liste via la variable headers
    with filepath.open (mode="w", newline="", encoding = "utf-8-sig") as fichier:
        writer = csv.DictWriter(fichier, fieldnames = headers, delimiter =";")     # Le fichier s'ouvre, les entêtes sont générés avec .writeheader() et les données sont implantées via writerows(liste)
        writer.writeheader()
        writer.writerows(list_to_implement)
    return


#main

base_dir = Path(__file__).resolve().parent
url = "https://books.toscrape.com"
scrapping_progess = 0
books_quantity = 0
response = requests.get(url)
if response.ok:
    print("Scrapping on " + url + " launched")
    page_content = BeautifulSoup(response.content, "lxml")
    if page_content.find("form", method="get", class_="form-horizontal"):
        books_quantity = page_content.find("form", method="get", class_="form-horizontal").find_next("strong").get_text(strip=True)
    else:
        print("Error during searching the book quantity : form, method=get, class_=form-horizontal).find_next(strong)")
    if page_content.find("ul", class_="nav nav-list").find_next("ul").find("li"):
        for element in page_content.find("ul", class_="nav nav-list").find_next("ul").find_all("li"):
            pages_urls=[]
            new_category_url = (url + "/" + element.find("a")["href"])
            category_name = (element.find("a").get_text(strip = True))
            print("\nCategory " + category_name + "\n")
            category_page_response = requests.get(new_category_url)
            if category_page_response.ok:
                category_page_content = BeautifulSoup(category_page_response.content, "lxml")
                pages_urls.extend(check_category_pages_quantity(new_category_url,category_page_content))
                products_urls = collect_urls_products(pages_urls)
                books_infos_per_category = scrapping_infos_per_category(products_urls, category_name)
                scrapping_progess += len(books_infos_per_category)
                print("\nGeneral scrapping progress : " + str(round(scrapping_progess / int(books_quantity) *100, 2)) + "%\n")
                export_csv(category_name +".csv", books_infos_per_category, base_dir)
                print(category_name +".csv succesfully updated\n")
                download_book_image(books_infos_per_category, category_name, base_dir)
                print("\nImages for each book in "+ category_name + " category successfully downloaded\n")
    else:
        print("Error during searching categories : ul, class_=nav nav-list).find_next(ul).find(li)")
        exit
    print("Scrapping ended, all CSV files and images updated")