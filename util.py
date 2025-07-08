import csv
import json
from json import loads
from time import sleep

import httpx
from bs4 import BeautifulSoup
from rapidfuzz import process, fuzz

with open('countries.json', 'r', encoding='utf-8') as f:
    countries = json.load(f)

names = [c['name'] for c in countries]

client = httpx.Client(http2=True)

status = ['UNAUTHORIZED']
USERNAME = "API365MD"
PASSWORD = "TBXml865gh7]#"
MICRO_SITE_ID = "tbrooms"


searchHotelHeaders = {
    "Accept": "application/xml, text/xml, */*; q=0.01",
    "Accept-Language": "en,en-US;q=0.9",
    "Cache-Control": "no-cache",
    "DNT": "1",
    "Faces-Request": "partial/ajax",
    "Origin": "https://tbrooms.me",
    "Pragma": "no-cache",
    "Referer": "https://tbrooms.me/admin/hotel-contract/hotel-list.xhtml",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "Sec-GPC": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest"
}


def login():
    r1 = client.get("https://tbrooms.me/login.xhtml")

    global jsessionId, flashRenderMapToken, backendUrl, userID

    soup = BeautifulSoup(r1.text, "html.parser")
    viewstate = soup.find("input", {"name": "javax.faces.ViewState"})["value"]

    headers = {
        "Accept": "application/xml, text/xml, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en,en-US;q=0.9",
        "Cache-Control": "no-cache",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "DNT": "1",
        "Faces-Request": "partial/ajax",
        "Origin": "https://tbrooms.me",
        "Pragma": "no-cache",
        "Priority": "u=1, i",
        "Referer": "https://tbrooms.me/admin/hotel-contract/hotel-list.xhtml",
        "Sec-CH-UA": '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
        "Sec-CH-UA-Mobile": "?0",
        "Sec-CH-UA-Platform": '"Windows',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Sec-GPC": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest"
    }
    data = {
        "javax.faces.partial.ajax": "true",
        "javax.faces.source": "login-form:login-content:login:signin",
        "javax.faces.partial.execute": "login-form:login-content:login-form-content login-form:login-content:login:login-form-content",
        "javax.faces.partial.render": "login-form:login-content:login-form-content login-form:login-content:login:login-form-content",
        "login-form:login-content:login:signin": "login-form:login-content:login:signin",
        "micrositeId": MICRO_SITE_ID,
        "login-form:login-content:login:requestURI": "/home.xhtml",
        "login-form:login-content:login:Email": "Demo!",
        "login-form:login-content:login:j_password": "TBrooms@@345",
        "login-form:login-content:login:remember": "true",
        "javax.faces.ViewState": viewstate
    }

    client.post("https://tbrooms.me/login.xhtml", headers=headers, data=data)



def getSeachHotelsCsrfToken():
    url = "https://tbrooms.me/admin/hotel-contract/hotel-list.xhtml"

    r1 = client.get(url)

    soup = BeautifulSoup(r1.text, "html.parser")
    viewstate = soup.find("input", {"name": "javax.faces.ViewState"})["value"]
    return viewstate


def searchHotels(hotelName, viewState, cityCountry, cityCode):
    url = "https://tbrooms.me/admin/hotel-contract/hotel-list.xhtml"

    files = {
        "javax.faces.partial.ajax": (None, "true"),
        "javax.faces.source": (None, "SearchMasterHotel:FormAdminSearchHotel:masterList:searchButton"),
        "javax.faces.partial.execute": (None, "SearchMasterHotel:FormAdminSearchHotel:masterList"),
        "javax.faces.partial.render": (None, "SearchMasterHotel:FormAdminSearchHotel:masterList"),
        "SearchMasterHotel:FormAdminSearchHotel:masterList:searchButton": (None, "SearchMasterHotel:FormAdminSearchHotel:masterList:searchButton"),
        "SearchMasterHotel:FormAdminSearchHotel:masterList:destination_input": (None, cityCountry),
        "SearchMasterHotel:FormAdminSearchHotel:masterList:destination_hinput": (None, cityCode),
        "SearchMasterHotel:FormAdminSearchHotel:masterList:hotelName": (None, hotelName),
        "SearchMasterHotel:FormAdminSearchHotel:masterList_rppDD": (None, "20"),
        "SearchMasterHotel:FormAdminSearchHotel:masterList_selection": (None, ""),
        "javax.faces.ViewState": (None, viewState)
    }

    response = client.post(url, files=files, headers=searchHotelHeaders)

    print("Status Code:", response.status_code)
    print(response.text)

    while "</redirect>" in response.text:
        login()
        response = client.post(url, files=files, headers=searchHotelHeaders)

        print("Status Code:", response.status_code)
        print(response.text)
        sleep(5)

    return response.text


def extractHotels(xml_string):
    """
    Given the full <partial-response> XML as a string,
    returns a list of dicts: [{'data_rk': ..., 'name': ..., 'address': ...}, …].
    """
    # 1) Parse the outer XML to grab just the CDATA block under the masterList update
    outer = BeautifulSoup(xml_string, "lxml-xml")
    upd = outer.find("update", {"id": "SearchMasterHotel:FormAdminSearchHotel:masterList"})
    if not upd or not upd.string:
        return []
    html_fragment = upd.string

    # 2) Parse that fragment as HTML to get the table rows
    table = BeautifulSoup(html_fragment, "html.parser")
    rows = table.find_all("tr")

    results = []
    for tr in rows:
        data_rk = tr.get("data-rk", "").strip()
        tds = tr.find_all("td")
        if len(tds) < 3:
            continue

        name = tds[0].get_text(strip=True)
        address = tds[2].get_text(strip=True)

        results.append({
            "data_rk": data_rk,
            "name": name,
            "address": address
        })
    return results


def extractHotelDetails(xml_string):
    """
    Parses the PrimeFaces partial-response XML and pulls out from the MasterHotelDialog:
      - phone number
      - full address and the part after the '-'
      - coordinates
      - description text
      - all image links from data-src attributes
    Returns a dict with keys:
      phone, address, address_after_dash, coordinates, description, images
    """
    # 1) Grab the CDATA HTML for the modal
    outer = BeautifulSoup(xml_string, "lxml-xml")
    upd = outer.find("update", {"id": "MasterHotelDialog:MasterHotelDialog"})
    if not upd or not upd.string:
        return {}

    html = upd.string
    soup = BeautifulSoup(html, "html.parser")

    details = {}

    # Phone number
    phone_icon = soup.find("i", class_="fa-phone")
    if phone_icon and phone_icon.next_sibling:
        details["phone"] = phone_icon.next_sibling.strip()

    # Address and part after '-'
    addr_icon = soup.find("i", class_="fa-address")
    if addr_icon and addr_icon.next_sibling:
        full_addr = addr_icon.next_sibling.strip()
        parts = full_addr.split("-", 1)
        details["address"] = parts[0].strip() if len(parts) > 1 else ""
        details["address_after_dash"] = parts[1].strip() if len(parts) > 1 else ""

    # Coordinates
    coord_icon = soup.find("i", class_="fa-location-dot")
    if coord_icon:
        coord_container = coord_icon.parent  # the <div> wrapping the icon + text + <a>
        a_tag = coord_container.find("a", href=True)
        if a_tag:
            # href looks like ".../maps/place/41.04028,28.988235"
            coords = a_tag["href"].split("/place/")[-1]
        else:
            # fallback: grab the text node(s) before the <a>
            texts = [t for t in coord_container.stripped_strings
                     if "," in t and not t.startswith("http")]
            coords = texts[0] if texts else ""
        coordinatesParts = coords.split(",", 1)
        details["latitude"] = coordinatesParts[0]
        details["longitude"] = coordinatesParts[1]

    # Description (long text block)
    desc_div = soup.find("div", class_="u-white-space--prewrap")
    if desc_div:
        # preserve line breaks if any
        details["description"] = desc_div.get_text("\n", strip=True)

    # Images (data-src attrs)
    details["images"] = [
        img["data-src"]
        for img in soup.find_all("img", attrs={"data-src": True})
    ]

    return details


def fetchHotel(masterId, viewState):
    url = "https://tbrooms.me/admin/hotel-contract/hotel-list.xhtml"

    files = {
        "javax.faces.partial.ajax": (None, "true"),
        "javax.faces.source": (None, "SearchMasterHotel:FormAdminSearchHotel:masterList"),
        "javax.faces.partial.execute": (None, "SearchMasterHotel:FormAdminSearchHotel:masterList"),
        "javax.faces.partial.render": (None, "MasterHotelDialog:MasterHotelDialog"),
        "javax.faces.behavior.event": (None, "rowSelect"),
        "javax.faces.partial.event": (None, "rowSelect"),
        "SearchMasterHotel:FormAdminSearchHotel:masterList_instantSelectedRowKey": (None, str(masterId)),
        "SearchMasterHotel:FormAdminSearchHotel:masterList:destination_input": (None, ""),
        "SearchMasterHotel:FormAdminSearchHotel:masterList:destination_hinput": (None, ""),
        "SearchMasterHotel:FormAdminSearchHotel:masterList:hotelName": (None, ""),
        "SearchMasterHotel:FormAdminSearchHotel:masterList_rppDD": (None, "20"),
        "SearchMasterHotel:FormAdminSearchHotel:masterList_selection": (None, str(masterId)),
        "javax.faces.ViewState": (None, viewState),
    }

    response = client.post(url, files=files, headers=searchHotelHeaders)

    print("Status Code:", response.status_code)
    print(response.text)

    while "</redirect>" in response.text:
        login()
        response = client.post(url, files=files, headers=searchHotelHeaders)

        print("Status Code:", response.status_code)
        print(response.text)
        sleep(5)

    return response.text


def getAuthToken(username, password, micrositeId):
    if username is None:
        raise Exception("Username is not provided")
    if password is None:
        raise Exception("Password is not provided")
    if micrositeId is None:
        raise Exception("MicrositeId is not provided")

    body = {
        "username": username,
        "password": password,
        "micrositeId": micrositeId
    }

    response = client.post("https://online.travelcompositor.com/resources/authentication/authenticate", json=body)
    return response.json()['token']


def getSuppliers(authToken):
    response = client.get("https://online.travelcompositor.com/resources/suppliers", headers={'auth-token': authToken})
    return response.text

def match_country(query: str):
    match, score, idx = process.extractOne(
        query, names, scorer=fuzz.token_sort_ratio
    )
    return {
        'name': match,
        'code': countries[idx]['code'],
        'score': score
    }

def createContractHotel(authToken, supplierId, providerCode, hotelDetails, countryName):

    country = match_country(countryName)
    print("Resolved country:", country)

    body = {
        "providerCode": providerCode,
        "hotelname": "TEST-InterContinental",
        "latitude": hotelDetails['latitude'],
        "longitude": hotelDetails['longitude'],
        "address": {
            "address": hotelDetails['address'],
            "locationName": hotelDetails['address_after_dash'],
            "country": country['code'],
            "phone": hotelDetails['phone']
        },
        "category": "5 STARS",
        "currency": "USD",
        "rooms": [{
            "name": "Room1",
            "typeId": "1",
            "providerCode": providerCode,
            "distributions": [{'adults': 1, 'children': 1}]
        }],
        "mealPlans": [{"mealPlan": "ROOM_ONLY", "basePrice": 23.2, "adultPrices": [12.1, 12.3, 12.5, 12.7],
                       "childPrices": [13.1, 13.3, 13.5]}],
        "descriptions": [{'language': "en", "description": "This is a test for creating an hotel contract"}],
        "images": [
            "https://media.istockphoto.com/id/183412466/photo/eastern-bluebirds-male-and-female.jpg?s=612x612&w=0&k=20&c=6_EQHnGedwdjM9QTUF2c1ce7cC3XtlxvMPpU5HAouhc="]
    }

    response = client.post(f"https://online.travelcompositor.com/resources/hotel/{supplierId}",
                           headers={'auth-token': authToken}, json=body)
    return response.text


token = getAuthToken(username=USERNAME, password=PASSWORD, micrositeId=MICRO_SITE_ID)
suppliers = loads(getSuppliers(authToken=token))

chosenSupplierId = None

for supplier in suppliers:
    if supplier['commercialName'] == "Karnak DMC":
        chosenSupplierId = supplier['id']

login()
print(f"Supplier ID: {chosenSupplierId}")
viewState = getSeachHotelsCsrfToken()
masterId = extractHotels(searchHotels("InterContinent", viewState=viewState))[0]['data_rk']
print("MASTER ID: ", masterId)
hotel = fetchHotel(masterId, viewState=viewState)
print("HOTEL: ", hotel)
hotelDetails = extractHotelDetails(hotel)
print("EXTRACTED HOTEL DETAILS: ", hotelDetails)
print(createContractHotel(authToken=token, supplierId=chosenSupplierId, providerCode=masterId,
                          hotelDetails=hotelDetails, countryName="Turkey"))
