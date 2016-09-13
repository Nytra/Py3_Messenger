# Messenger Update Tool
__author__ = "Sam Scott"
__email__ = "samueltscott@gmail.com"
repo = "https://github.com/Nytra/messenger"

from urllib import request
import zipfile, io, os

def update():
    try:
        print("Downloading repository...")
        r = request.urlopen("https://github.com/Nytra/messenger/archive/master.zip")
        print("Extracting...")
        with zipfile.ZipFile(io.BytesIO(r.read())) as z:
            z.extractall()
        print("Moving files...")
        cmd = "move \"{}\\messenger-master\\*\" \"{}\"".format(os.path.abspath(""), os.path.abspath(""))
        os.system(cmd)
        cmd = "rmdir \"{}\\messenger-master\"".format(os.path.abspath(""))
        print("Cleaning up...")
        os.system(cmd)
        with open("version_info.txt", "w") as f:
            f.write(online_vnum)
        input("Installation complete.\n\nPress enter to quit . . .")
    except:
        print("An error occurred during the installation procedure. Your files may be corrupt.")

if __name__ == "__main__":
    update()
