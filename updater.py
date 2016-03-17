from urllib import request
import zipfile, io, os, time,string

def get_current_version_number():
    digits = string.digits
    commit_number = ""
    url = "https://github.com/Nytra/messenger/pulse"
    response = request.urlopen(url)
    data = response.readlines()
    for index, line in enumerate(data):
        if "class=\"section diffstat-summary\"" in line.decode("utf-8"):
            data = data[index:index+4]
            break
    for line in data:
        if "<strong><span class=\"text-emphasized\">" in line.decode("utf-8"):
            found = line.decode("utf-8")
            break
    for char in found:
        if char in digits:
            commit_number += char
    return commit_number

def get_local_version_number():
    try:
        with open("version_info.txt", "r") as f:
            local_version_number = f.read().strip()
    except:
        local_version_number = 0
    return local_version_number

def update():
    try:
        print("Downloading master zip file...")
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
        print("Done.")
        with open("version_info.txt", "w") as f:
            f.write(online_vnum)
        input("Installation complete.\n\nPress enter to quit . . .")
    except:
        print("An error occurred during the installation procedure. Your files may be corrupt.")

if __name__ == "__main__":
    print("Checking for updates...")
    online_vnum = get_current_version_number()
    local_vnum = get_local_version_number()
    if local_vnum != online_vnum:
        print("An update is available.\nYou have missed {} commits.\n\nDownload? [Y/N]: ".format(int(online_vnum) - int(local_vnum)), end = "")
        choice = input().lower().strip()
        if choice == "y":
            update()
    else:
        print("You already have the latest version. Would you like to update anyway? [Y/N]: ", end = "")
        choice = input().lower().strip()
        if choice == "y":
            update()
        
        
