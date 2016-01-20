import requests
#img_path = '/Users/philokey/Pictures/doge.jpg'
#img_path = '/Users/philokey/Pictures/in.png'
img_path = '/Users/philokey/comic.py'
img_path = '/Users/philokey/test.txt'
url = 'http://127.0.0.1:8080'
# img = {'type':'frame','file':open(img_path, 'rb')}
img = {'file':open(img_path, 'rb')}
pdata = {'key':'val'}
# img = {'file':open(img_path, 'rb')}
print(img)

r = requests.post(url, data = pdata, files=img)
print(r.text)