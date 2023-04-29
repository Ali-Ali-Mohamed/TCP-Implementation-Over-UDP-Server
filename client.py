import requests

# The API endpoint
url1 = "http://localhost:63342/Final%20Network/venv/page1.html?_ijt=7pe1s23aernairtb0pi4bg0p9v&_ij_reload=RELOAD_ON_SAVE"
url2 = "http://localhost:63342/Final%20Network/venv/page1.html?_ijt=7pe1s23aernairtb0pi4bg0p9v&_ij_reload=RELOAD_ON_SAVE"

fname = 'Ali'
lname = 'Mohamed'
payload = {"firstName": fname, "lastName": lname}

response = requests.get(url1, params=payload)
print(response.url)
print(response.status_code)


response = requests.post(url2, data=payload)
print(response.url)
print(response.status_code)

