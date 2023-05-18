from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
# import html5lib
import lxml
import re
import time
from datetime import datetime
from random import randrange
import csv

SITE_URL = "https://www.abcam.com/"
# TODO rewrite explicit waits
# TODO add full text
#

def get_source_html(art):
    time.sleep(3)
    try:
        driver.find_element(By.ID, "searchfieldtop").send_keys(art + Keys.ENTER)
    except:
      print('No searchfield')
    time.sleep(5)
    return driver.page_source

def get_soup(html):
    try:
        soup = BeautifulSoup(html, "lxml")
        return soup
    except:
        print('No soup!')

def get_art_structure(soup, art):

    reactivity_dict = {
        "Human": "человек",
        "Mouse": "мышь",
        "Rat": "крыса",
        "Dog": "собака",
        "African green monkey": "зелёная мартышка",
        "Recombinant fragment": "рекомбинантный фрагмент"
    }
    application_dict = {
        "WB": "вестерн-блоттинга",
        "IHC": "иммуногистохимии",
        "IHC-P": "иммуногистохимии на парафиновых срезах",
        "IF/ICC": "иммунофлуоресцентного/иммуноцитохимического анализа",
        "ICC/IF": "иммунофлуоресцентного/иммуноцитохимического анализа",
        "IF": "иммунофлуоресцентного анализа",
        "IP": "иммунопреципитации",
        "ChIP": "иммунопреципитации хроматина",
        "ChIP-seq": "иммунопреципитации хроматина и высокоэффективного секвенирования",
        "RIP": "иммунопреципитации РНК",
        "Flow Cyt": "проточной цитометрии",
        "Flow Cyt (Intra)": "проточной цитометрии (Intra)",
        "ELISA": "ИФА",
        "MeDIP": "иммунопреципитации метилированной ДНК",
        "Nucleotide Array": "исследования нуклеотидных последовательностей",
        "DB": "дот-блоттинга",
        "FACS": "сортировки клеток, активируемых флуоресценцией",
        "CoIP": "коиммунопреципитации",
        "CUT&Tag": "CUT&Tag секвенирование",
        "meRIP": "иммунопреципитации метилированной РНК"
    }
    title_cont = soup.find("div", class_="title-container")
    if title_cont:
        title = title_cont.find("h1", class_="title").get_text()
    else:
        print("No title")
        title = ""

    volume_cont = soup.find("div", class_="size-price-placeholder")
    if volume_cont:
        volumes = []
        prices = []
        if volume_cont:
            volumes.append(volume_cont.get_text().strip().replace("µ", "u"))
            time.sleep(3)
            price_cont = soup.find("span", class_="price-holder")
            prices.append(price_cont.get_text().strip())
            # print(prices)
        else:
            volume_radios = soup.select("span.product-size > span:nth-of-type(1)")
            volumes = [vol.get_text(" ").strip().replace("µ", "u") for vol in volume_radios]
            time.sleep(3)
            price_radios = soup.find_all("span", class_="price")
            prices = [price.get_text(" ").strip() for price in price_radios]
            # print(prices)
    else:
        print('No volume, no price')
        prices = []
        volumes = []

    descr_h3 = soup.find("h3", string="Description")
    if descr_h3:
        descr = descr_h3.find_next_sibling("div", class_="value").get_text()
        host = descr[:descr.find(" ")]
        clonality = descr.split(" ")[1]
        antigen = descr[descr.find(" to ") + 4:]
    else:
        print('No descr, host, clonality, antigen')
        descr = ""
        host = ""
        clonality = ""
        antigen = ""

    if clonality != "polyclonal":
        clone_h3 = soup.find("h3", string="Clone number")
        clone = clone_h3.find_next_sibling("div", class_="value").get_text()
    else:
        clone = ""
        print('No clone num')


    form_h3 = soup.find("h3", string="Form")
    if form_h3:
        form = form_h3.find_next_sibling("div", class_="value").get_text()
    else:
        print('No form')
        form = ""

    time.sleep(1)
    reactivity_cont = soup.find("section", id="key-features")
    reactivity = ""
    reactivity_ru = ""
    if reactivity_cont:
        reactivity_li = reactivity_cont.find_all("li")
        for li in reactivity_li:
            if li.find(string=re.compile("Reacts with:")):
                reactivity_full = li.get_text().strip()
                reactivity = reactivity_full[14:]
                # print(reactivity)
        reactivity_ru = ", ".join([reactivity_dict.get(w.strip(), w.strip()) for w in reactivity.split(",")])
    else:
        print('No reactivity')

    storage_h3 = soup.find("h3", string="Storage instructions")
    if storage_h3:
        storage = storage_h3.find_next_sibling("div", class_="value").get_text()
    else:
        print('No storage')
        storage = ""

    try:
        storage_buff_h3 = soup.find("h3", string="Storage buffer")
        storage_buff = storage_buff_h3.find_next_sibling("div", class_="value").get_text(" ").strip()
    except:
        print('No buffer')
        storage_buff = ""

    try:
        conc_h3 = soup.find("div", string="Concentration")
        conc_list = conc_h3.find_next_sibling("div", class_="value").find("ul").find_all("li")
        concs = [li.get_text().strip() for li in conc_list]
        conc = "\n".join(concs)
    except:
        print('No conc')
        conc = ""

    appl_cont = soup.find("div", id="description_applications")
    dilus_short = []
    ihc_dil = ""
    if appl_cont:
        appl_tbl = appl_cont.find("table", class_="table")
        appl_trs = appl_tbl.find_all("tr")
        tbl_names = []
        tbl_diluts = []
        appls = ""
        dilus = ""
        for tr in appl_trs:
            tbl_name = [td.get_text().strip() for td in tr.find_all("td", class_="name")]
            if len(tbl_name) > 0:
                tbl_names.extend(tbl_name)
            appls = "\n".join(tbl_names)
            tbl_dilut = [td.get_text(" ").strip() for td in tr.find_all("td", class_="value value2--addon")]
            if len(tbl_dilut) > 0:
                tbl_diluts.extend(tbl_dilut)
            dilus = "\n".join(tbl_diluts)
        if len(tbl_names) == len(tbl_diluts):
            for i in range(len(tbl_names)):
                dilus_short.append(tbl_names[i] + " " + tbl_diluts[i][:tbl_diluts[i].find(".")])
                if tbl_names[i] == "IHC" or tbl_names[i]=="IHC-P":
                    ihc_dil = tbl_diluts[i][:tbl_diluts[i].find(".")]
        print(dilus_short)
        print(ihc_dil)
        appls_ru = ", ".join([application_dict.get(w.strip(), w.strip()) for w in appls.split("\n")])
    else:
        print('No app-dil')
        appls = ""
        appls_ru = ""
        dilus = ""
    if len(dilus_short) > 0:
        text = "\n".join(dilus_short) + "\n" + reactivity
    else:
        text = "\n".join(dilus) + "\n" + reactivity

    dict_art_list = []
    for i in range(0, len(volumes)):
        dict_art = {
            "Article": art.strip(),
            "Volume": volumes[i].split(" ")[0],
            "Volume units": volumes[i].split(" ")[1],
            "Antigen": antigen,
            "Host": host,
            "Clonality": clonality,
            "Clone_num": clone,
            "Text": text,
            "Applications_ru": appls_ru,
            "Reactivity_ru": reactivity_ru,
            "Title": title[:title.rfind("(")].strip(),
            "IHC dilution": ihc_dil,
            "Applications": appls,
            "Dilutions": dilus,
            "Reactivity": reactivity,
            "Form": form,
            "Storage instructions": storage,
            "Storage buffer": storage_buff,
            "Concentration": conc,
            "Price": prices[i],
        }
        dict_art_list.append(dict_art)
    return dict_art_list

def write_csv(result):
    date = datetime.now().strftime('%d.%m.%Y_%H.%M')
    with open("data-abcam\\Abcam_{}.csv".format(date), "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=result[0].keys())
        writer.writeheader()
        writer.writerows(result)

def main(arts):
    result = []
    counter = 0
    for art in arts:
        time.sleep(randrange(3, 5))
        counter += 1
        print(counter, " art No ", art)
        src = get_source_html(art)
        soup = get_soup(src)
        art_structure = get_art_structure(soup, art)
        result.extend(art_structure)
    return result

service = Service("C:\\Users\\Public\\Parsing programs\\chromedriver.exe")
options = webdriver.ChromeOptions()

options.add_argument("--disable-extensions")
# options.add_argument("--disable-gpu")
options.add_argument("--headless")
options.add_argument("--ignore-certificate-errors-spki-list")
options.add_argument("--ignore-ssl-errors")
options.add_argument("--disable-infobars")
options.add_argument('--log-level=3')
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36")

driver = webdriver.Chrome(service=service, options=options)
print("Start browser")
start_time = datetime.now()
driver.maximize_window()
driver.get(SITE_URL)
driver.implicitly_wait(5)
time.sleep(1)
driver.find_element(By.ID, "onetrust-accept-btn-handler").click()
time.sleep(1)
driver.find_element(By.XPATH, "//*[@id='pws_quick_menu_container']/div[1]/div[2]/a").click()
time.sleep(1)
driver.find_element(By.ID, "country__input-text").find_element(By.CLASS_NAME, "ui-autocomplete-input").send_keys("Germany" + Keys.ARROW_DOWN + Keys.ENTER)
time.sleep(1)

try:
    print("Введите список артикулов:")
    articles = [str(art) for art in input().split(",")]
    result_parse = main(articles)
    finish_time = datetime.now()
    spent_time = finish_time - start_time
    print(spent_time)
    # print(result_parse)
    write_csv(result_parse)

except Exception as ex:
    print(ex)

finally:
    # driver.close()
    driver.quit()
