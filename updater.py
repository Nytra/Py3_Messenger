from urllib import request
import zipfile, io, os, time
print("Extracting file...")
r = request.urlopen("https://github.com/Nytra/messenger/archive/master.zip")
with zipfile.ZipFile(io.BytesIO(r.read())) as z:
    z.extractall()
files = ["updater.py", "messenger.py", "server.py"]
print(os.path.abspath(""))
time.sleep(2)
for file in files:
    cmd = "move \"{}\\messenger-master\\{}\" \"{}\"".format(os.path.abspath(""), file, os.path.abspath(""))
    print(cmd)
    input()
    os.system(cmd)
cmd = r"rmdir /Q /S {}\messenger-master".format(os.path.abspath(""))
print(cmd)
os.system(cmd)

print("Done.")
