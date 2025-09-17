from storage import save_to_file, load_from_file

def add_note(title, text):
    note = f"{title}|{text}"
    save_to_file(note)

def show_notes():
    for raw in load_from_file():
        title, text = raw.strip().split("|")
        print(f"{title}: {text}")