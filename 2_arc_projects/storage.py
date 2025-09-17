def save_to_file(text):
    with open("notes.txt", "a", encoding="utf-8") as f:
        f.write(text + "\n")

def load_from_file():
    with open("notes.txt", encoding="utf-8") as f:
        return f.readlines()