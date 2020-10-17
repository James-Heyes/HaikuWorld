from bs4 import BeautifulSoup
import re
import requests

replacements = [(r'[^\S\r\n]{2,}', ''),
                (r'\n{2,}', '\n\n')]

url = "https://www.poetryfoundation.org/search?query=haiku&refinement=poems&page="

poems = ''

for index in range(10):
    page = requests.get(url+str(index))
    if page.status_code != 404:
        soup = BeautifulSoup(page.content, 'html.parser').find_all('div', class_='c-feature-hd')

        links = ["https://www.poetryfoundation.org/" + linkTag.find('a')['href'] for linkTag in soup]

        for link in links:
            poemPage = requests.get(link)
            poem = BeautifulSoup(poemPage.content, 'html.parser').find('div', class_="c-feature").text
            for old, new in replacements:
                poem = re.sub(old, new, poem)
            poem += '\n<|endoftext|>'
            poems += poem
    else:
        break


with open("PoemOutput.txt", 'w') as outfile:
    outfile.write(poems)


