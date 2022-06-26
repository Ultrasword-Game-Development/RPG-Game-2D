import os

DELETE_FILE = "__pycache__"


cwd = os.getcwd()

def clean_pycache(path):
    count = 0
    # for every file
    for file in os.listdir(path):
        # if not folder, then check if it is a __pycache__ folder
        if file == DELETE_FILE:
            count += clean_folder(os.path.join(path, file))
            os.rmdir(os.path.join(path, file))
        # check if file is a folder
        elif os.path.isdir(file):
            count += clean_pycache(os.path.join(path, file))
    return count


def clean_folder(folder_path):
    count = 0
    for file in os.listdir(folder_path):
        os.remove(os.path.join(folder_path, file))
        count += 1
    return count

print(f"Cleaning all files from `{cwd}`")
count = clean_pycache(cwd)
print(f"Finished cleaning!\nCleaned {count} files!")

