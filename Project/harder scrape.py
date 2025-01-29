from urllib.request import urlopen

url = "http://olympus.realpython.org/profiles/poseidon"
page = urlopen(url)
html_bytes = page.read()
html = html_bytes.decode("utf8")

print(html)
title_index = html.find("<title >")
end_index = html.find("</title>")
start_index = title_index + len("<title >")
title = html[title_index:end_index]
print(title)
