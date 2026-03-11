from bs4 import BeautifulSoup

def find_context():
    with open("opentable_search.html", "r", encoding="utf-8") as f:
        html = f.read()
    
    soup = BeautifulSoup(html, "html.parser")
    # Find string
    element = soup.find(string=lambda text: text and "Gran Morsi" in text)
    if element:
        print(f"Parent tag: {element.parent.name}")
        print(f"Parent attrs: {element.parent.attrs}")
        print(f"Grandparent tag: {element.parent.parent.name}")
        print(f"Grandparent attrs: {element.parent.parent.attrs}")
        # print snippet
        print(f"Snippet: {str(element.parent)[:200]}")
    else:
        print("Not found in DOM structure (might be in script only).")

if __name__ == "__main__":
    find_context()
