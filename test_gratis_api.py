import urllib.request
import re
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

url = "https://www.gratis.com/cilt-bakimi-c-300"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})

try:
    response = urllib.request.urlopen(req)
    html = response.read().decode('utf-8')
    
    # Find all hrefs
    links = re.findall(r'href="([^"]+-p-\d+)"', html)
    links = list(set(links))
    print(f"Found {len(links)} product links directly in the HTML!")
    for l in links[:5]:
        print(l)
        
    # Also find next.js chunk data just in case
    # Let's search for "product" in next chunks
    matches = re.findall(r'\\"(name|title)\\":\\"([^\\"]+)\\"', html)
    print(f"Found {len(matches)} name/title matches in JSON chunks")
    for m in matches[:10]:
        print(m)

except Exception as e:
    print("Error:", str(e))
