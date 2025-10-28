import requests

client_id = "sbKAsw4mqHHqT5AocOyjcScHldW0xCx1"
client_secret = "5htTldQeWUr48sr4"

url = "https://test.api.amadeus.com/v1/security/oauth2/token"
data = {
  "grant_type": "client_credentials",
  "client_id": client_id,
  "client_secret": client_secret
}

resp = requests.post(url, data=data)
print(resp.status_code, resp.json())
