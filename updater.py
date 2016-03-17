from urllib import request

response = request.urlopen('https://github.com/Nytra/messenger/archive/master.zip')
data = response.read()
with open("master.zip", 'w') as f:
    f.write(data)
