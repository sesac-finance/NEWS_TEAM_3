import requests

r = requests.post("http://127.0.0.1:8000/api/v1/articles/")

print(r.status_code)
print(r.text)