from urllib import request
import zipfile, io, os, time
print("Downloading master zip file...")
r = request.urlopen("https://github.com/Nytra/messenger/archive/master.zip")
print("Extracting...")
with zipfile.ZipFile(io.BytesIO(r.read())) as z:
    z.extractall()
files = ["updater.py", "messenger.py", "server.py", "README.md"]
time.sleep(2)
print("Moving files...")
for file in files:
    cmd = "move \"{}\\messenger-master\\{}\" \"{}\"".format(os.path.abspath(""), file, os.path.abspath(""))
    os.system(cmd)
cmd = "rmdir \"{}\\messenger-master\"".format(os.path.abspath(""))
print("Cleaning up...")
os.system(cmd)

print("Done.")
