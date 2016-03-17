from urllib import request
import zipfile, io
print("Extracting file...")
r = request.urlopen("https://github.com/Nytra/messenger/blob/master/master.zip?raw=true")
with zipfile.ZipFile(io.BytesIO(r.read())) as z:
    z.extractall()
print("Done.")
