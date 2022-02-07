'''
import webbrowser
from googlesearch import search
chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'
# to search
query = "cmd.exe"

for j in search(query, tld="co.in", num=1, stop=1, pause=2):
    print(j)
    webbrowser.get(chrome_path).open(j)
'''


import os, psutil
process = psutil.Process(os.getpid())
print(process.memory_info().rss)