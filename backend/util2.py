# util2.py

import csv
import json
from json import loads
from time import sleep

import httpx
from bs4 import BeautifulSoup
from rapidfuzz import process, fuzz
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path      # ← add this

# FastAPI app setup
app = FastAPI(
    title="TravelBureau Backend",
    description="Utilities & endpoints for hotel contract operations",
)

# Allow CORS from your Next.js frontend (adjust origin as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# compute the directory that this file lives in
BASE_DIR = Path(__file__).resolve().parent

# open countries.json from the same folder
with open(BASE_DIR / 'countries.json', 'r', encoding='utf-8') as f:
    countries = json.load(f)

# now build your list of names
names = [c['name'] for c in countries]
# HTTP client
client = httpx.Client(http2=True)

# Constants
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


### FastAPI Endpoints ###

@app.get("/search-countries")
def search_countries(query: str = Query(..., min_length=1)) -> list:
    """
    Return up to 3 best fuzzy matches for `query` against our country list.
    """
    matches = process.extract(
        query,
        names,
        scorer=fuzz.token_sort_ratio,
        limit=3
    )
    return [
        {"name": m, "code": countries[i]["code"], "score": s}
        for m, s, i in matches
    ]


### Utility functions ###

def login():
    client.cookies.clear()
    r1 = client.get("https://tbrooms.me/login.xhtml")

    soup = BeautifulSoup(r1.text, "html.parser")
    viewstate = soup.find("input", {"name": "javax.faces.ViewState"})["value"]

    headers = {
        **searchHotelHeaders,
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Priority": "u=1, i",
    }
    data = {
        "javax.faces.partial.ajax": "true",
        "javax.faces.source": "login-form:login-content:login:signin",
        "javax.faces.partial.execute":
            "login-form:login-content:login-form-content "
            "login-form:login-content:login:login-form-content",
        "javax.faces.partial.render":
            "login-form:login-content:login-form-content "
            "login-form:login-content:login:login-form-content",
        "login-form:login-content:login:signin":
            "login-form:login-content:login:signin",
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
    return soup.find("input", {"name": "javax.faces.ViewState"})["value"]


def extractDestinationAutocompleteItems(xml_text):
    soup = BeautifulSoup(xml_text, "xml")
    update = soup.find(
        "update",
        {"id": "SearchMasterHotel:FormAdminSearchHotel:masterList:destination"}
    )
    if not update:
        return []
    inner = BeautifulSoup(update.decode_contents(), "html.parser")
    items = []
    for li in inner.find_all("li"):
        v = li.get("data-item-value")
        l = li.get("data-item-label")
        if v and l:
            items.append((v, l))
    return items


def searchDestination(query):
    viewState = getSeachHotelsCsrfToken()
    url = "https://tbrooms.me/admin/hotel-contract/hotel-list.xhtml"
    files = {
        "javax.faces.partial.ajax": (None, "true"),
        "javax.faces.source":
            (None, "SearchMasterHotel:FormAdminSearchHotel:masterList:destination"),
        "javax.faces.partial.execute":
            (None, "SearchMasterHotel:FormAdminSearchHotel:masterList:destination"),
        "javax.faces.partial.render":
            (None, "SearchMasterHotel:FormAdminSearchHotel:masterList:destination"),
        "javax.faces.behavior.event": (None, "query"),
        "javax.faces.partial.event": (None, "query"),
        "SearchMasterHotel:FormAdminSearchHotel:masterList:destination_query":
            (None, query),
        "SearchMasterHotel:FormAdminSearchHotel:masterList:destination_input":
            (None, query),
        "SearchMasterHotel:FormAdminSearchHotel:masterList:destination_hinput":
            (None, query),
        "javax.faces.ViewState": (None, viewState),
    }
    resp = client.post(url, files=files, headers=searchHotelHeaders)
    while "</redirect>" in resp.text:
        login()
        sleep(1)
        resp = client.post(url, files=files, headers=searchHotelHeaders)
    return resp.text


def searchHotels(hotelName, viewState, cityCountry, cityCode):
    url = "https://tbrooms.me/admin/hotel-contract/hotel-list.xhtml"
    files = {
        "javax.faces.partial.ajax": (None, "true"),
        "javax.faces.source":
            (None, "SearchMasterHotel:FormAdminSearchHotel:masterList:searchButton"),
        "javax.faces.partial.execute":
            (None, "SearchMasterHotel:FormAdminSearchHotel:masterList"),
        "javax.faces.partial.render":
            (None, "SearchMasterHotel:FormAdminSearchHotel:masterList"),
        "SearchMasterHotel:FormAdminSearchHotel:masterList:searchButton":
            (None, "SearchMasterHotel:FormAdminSearchHotel:masterList:searchButton"),
        "SearchMasterHotel:FormAdminSearchHotel:masterList:destination_input":
            (None, cityCountry),
        "SearchMasterHotel:FormAdminSearchHotel:masterList:destination_hinput":
            (None, cityCode),
        "SearchMasterHotel:FormAdminSearchHotel:masterList:hotelName":
            (None, hotelName),
        "SearchMasterHotel:FormAdminSearchHotel:masterList_rppDD": (None, "20"),
        "SearchMasterHotel:FormAdminSearchHotel:masterList_selection": (None, ""),
        "javax.faces.ViewState": (None, viewState),
    }
    resp = client.post(url, files=files, headers=searchHotelHeaders)
    while "</redirect>" in resp.text:
        login()
        sleep(1)
        resp = client.post(url, files=files, headers=searchHotelHeaders)
    return resp.text


def extractHotels(xml_string):
    outer = BeautifulSoup(xml_string, "lxml-xml")
    upd = outer.find(
        "update",
        {"id": "SearchMasterHotel:FormAdminSearchHotel:masterList"}
    )
    if not upd or not upd.string:
        return []
    table = BeautifulSoup(upd.string, "html.parser")
    results = []
    for tr in table.find_all("tr"):
        rk = tr.get("data-rk", "").strip()
        tds = tr.find_all("td")
        if len(tds) < 3:
            continue
        results.append({
            "data_rk": rk,
            "name": tds[0].get_text(strip=True),
            "address": tds[2].get_text(strip=True)
        })
    return results


def extractHotelDetails(xml_string):
    outer = BeautifulSoup(xml_string, "lxml-xml")
    upd = outer.find("update", {"id": "MasterHotelDialog:MasterHotelDialog"})
    if not upd or not upd.string:
        return {}
    soup = BeautifulSoup(upd.string, "html.parser")
    details = {}
    # phone
    phone_icon = soup.find("i", class_="fa-phone")
    if phone_icon and phone_icon.next_sibling:
        details["phone"] = phone_icon.next_sibling.strip()
    # address / after dash
    addr_icon = soup.find("i", class_="fa-address")
    if addr_icon and addr_icon.next_sibling:
        full = addr_icon.next_sibling.strip()
        parts = full.split("-", 1)
        details["address"] = parts[0].strip()
        if len(parts) > 1:
            details["address_after_dash"] = parts[1].strip()
    # coords
    coord_icon = soup.find("i", class_="fa-location-dot")
    if coord_icon:
        parent = coord_icon.parent
        a = parent.find("a", href=True)
        coords = ""
        if a:
            coords = a["href"].split("/place/")[-1]
        else:
            texts = [t for t in parent.stripped_strings if "," in t and not t.startswith("http")]
            coords = texts[0] if texts else ""
        lat, lng = coords.split(",", 1)
        details["latitude"], details["longitude"] = lat, lng
    # description
    desc_div = soup.find("div", class_="u-white-space--prewrap")
    if desc_div:
        details["description"] = desc_div.get_text("\n", strip=True)
    # images
    details["images"] = [
        img["data-src"] for img in soup.find_all("img", attrs={"data-src": True})
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
        "SearchMasterHotel:FormAdminSearchHotel:masterList_instantSelectedRowKey":
            (None, str(masterId)),
        "SearchMasterHotel:FormAdminSearchHotel:masterList:destination_input": (None, ""),
        "SearchMasterHotel:FormAdminSearchHotel:masterList:destination_hinput": (None, ""),
        "SearchMasterHotel:FormAdminSearchHotel:masterList:hotelName": (None, ""),
        "SearchMasterHotel:FormAdminSearchHotel:masterList_rppDD": (None, "20"),
        "SearchMasterHotel:FormAdminSearchHotel:masterList_selection":
            (None, str(masterId)),
        "javax.faces.ViewState": (None, viewState),
    }
    resp = client.post(url, files=files, headers=searchHotelHeaders)
    while "</redirect>" in resp.text:
        login()
        sleep(1)
        resp = client.post(url, files=files, headers=searchHotelHeaders)
    return resp.text


def getAuthToken(username, password, micrositeId):
    if not username or not password or not micrositeId:
        raise ValueError("username, password and micrositeId are required")
    body = {"username": username, "password": password, "micrositeId": micrositeId}
    resp = client.post(
        "https://online.travelcompositor.com/resources/authentication/authenticate",
        json=body
    )
    resp.raise_for_status()
    return resp.json()["token"]


def getSuppliers(authToken):
    resp = client.get(
        "https://online.travelcompositor.com/resources/suppliers",
        headers={"auth-token": authToken}
    )
    resp.raise_for_status()
    return loads(resp.text)


def match_country(query: str):
    match, score, idx = process.extractOne(
        query, names, scorer=fuzz.token_sort_ratio
    )
    return {"name": match, "code": countries[idx]["code"], "score": score}


def createContractHotel(authToken, supplierId, providerCode, hotelDetails, countryName):
    country = match_country(countryName)
    body = {
        "providerCode": providerCode,
        "hotelname": hotelDetails.get("name", "UNKNOWN"),
        "latitude": hotelDetails["latitude"],
        "longitude": hotelDetails["longitude"],
        "address": {
            "address": hotelDetails["address"],
            "locationName": hotelDetails.get("address_after_dash", ""),
            "country": country["code"],
            "phone": hotelDetails.get("phone", "")
        },
        "category": "5 STARS",
        "currency": "USD",
        "rooms": [{
            "name": "Room1",
            "typeId": "1",
            "providerCode": providerCode,
            "distributions": [{"adults": 1, "children": 1}]
        }],
        "mealPlans": [{
            "mealPlan": "ROOM_ONLY",
            "basePrice": 23.2,
            "adultPrices": [12.1, 12.3, 12.5, 12.7],
            "childPrices": [13.1, 13.3, 13.5]
        }],
        "descriptions": [{
            "language": "en",
            "description": "Automated contract creation"
        }],
        "images": hotelDetails.get("images", [])
    }
    resp = client.post(
        f"https://online.travelcompositor.com/resources/hotel/{supplierId}",
        headers={"auth-token": authToken},
        json=body
    )
    resp.raise_for_status()
    return resp.text


if __name__ == "__main__":
    # Example script usage (won't run on import)
    token = getAuthToken(USERNAME, PASSWORD, MICRO_SITE_ID)
    suppliers = getSuppliers(token)
    chosen = next((s for s in suppliers if s["commercialName"] == "Karnak DMC"), None)
    if not chosen:
        print("Supplier not found")
    else:
        login()
        vs = getSeachHotelsCsrfToken()
        master = extractHotels(searchHotels("InterContinent", vs))[0]["data_rk"]
        raw = fetchHotel(master, vs)
        details = extractHotelDetails(raw)
        result = createContractHotel(token, chosen["id"], master, details, "Turkey")
        print("Contract creation response:", result)
