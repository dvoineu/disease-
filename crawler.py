import re
import requests
import html2text
from urllib.parse import urlparse
import Query
from collections import deque

import pickle



class Crawler:

    seed = ""
    visited = None
    proxy_orbit_key = None
    user_agent = ""
    proxy_orbit_url = ""
    text_converter = None
    count = 0
    q = deque()
    stop_link = {"language-assistance", "#"}

    def __init__(self, seed):
        self.seed = seed
        self.visited = set()
        self.text_converter = html2text.HTML2Text()
        self.text_converter.ignore_links = True
        self.index_to_html = {}
        self.index_to_summary = {}
        self.q.append((seed, 0))

        '''
        self.proxy_orbit_key = "pm0YOQUyUxphVV6Yd0LJDFKsNpDaeELG1Ld5hiDdrUs"
        self.user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"
        self.proxy_orbit_url = f"https://api.proxyorbit.com/v1/?token={self.proxy_orbit_key}&ssl=true&rtt=0.3&protocols=http&lastChecked=30"
        '''


    def extract_html(self, url):
        # No exception handel
        '''
        proxy_info = requests.get(self.proxy_orbit_url).json()
        proxy = proxy_info['curl']
        html = requests.get(url, headers={"User-Agent": self.user_agent}, proxies={"http": proxy, "https": proxy},
                            timeout=5)
        '''
        try:
            html = requests.get(url)
        except Exception as e:
            print(e)
            return ""
        return html.content.decode('latin-1')

    def extract_links(self, url):
        html = self.extract_html(url)
        parsed = urlparse(url)
        base = parsed.scheme + "://" + parsed.netloc
        links = re.findall('''<a\s+(?:[^>]*?\s+)?href="([^"]*)"''', html)
        for i, link in enumerate(links):
            if not urlparse(link).netloc:
                links[i] = base + link

        # no except mail address
        return set(links)

    def extract_metadata(self, url):
        html = self.extract_html(url)
        return dict(re.findall("<meta .*?name=[\"'](.*?)['\"].*?content=[\"'](.*?)['\"].*?>", html))

    def crawl(self):

        while self.q:
            curr = self.q.popleft()
            curr_link = curr[0]
            curr_depth = curr[1]

            if curr_depth >= 3:
                continue

            links = self.extract_links(curr_link)
            for link in links:
                if link in self.visited:
                    continue

                meta = self.extract_metadata(link)
                info = f"""Link: {link}    
                Description: {meta.get('description')}    
                Keywords: {meta.get('keywords')}    
                            """
                text = self.text_converter.handle(self.extract_html(link))

                if not meta or not text or len(text) < 100 or 'cdc.gov' not in link \
                        or '#' in link or 'language-assistance' in link:
                    continue

                print(info)
                print(curr_depth)

                file_name = 'small_data/' + str(self.count) + '.txt'
                output = open(file_name, 'w+')

                output.write(text)
                output.close()

                self.q.append((link, curr_depth + 1))
                self.visited.add(link)

                print(self.count)
                self.index_to_html[self.count] = link
                self.index_to_summary[self.count] = info
                self.count += 1
                # add code to save all info into local storage

    def start(self):
        self.crawl()


if __name__ == "__main__":
    # crawler = Crawler("https://www.cdc.gov/DiseasesConditions/")
    # crawler.start()
    search_engine = Query.Query("./data", True)

    results = search_engine.query('cough fever')
    for result in results:
        print(result)


