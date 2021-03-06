import re
import requests
import html2text
from urllib.parse import urlparse
import Query
from collections import deque

import threading





class Crawler:

    seed = ""
    visited = None
    # proxy_orbit_key = None
    # user_agent = ""
    # proxy_orbit_url = ""
    text_converter = None
    count = 0
    q = deque()
    # semaphore = threading.Semaphore(1)
    # threads = []

    def __init__(self, seed):
        self.seed = seed
        self.visited = set()
        self.text_converter = html2text.HTML2Text()
        self.text_converter.ignore_links = True
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
        return set(filter(lambda x: 'mailto' not in x, links))

    def extract_metadata(self, url):
        html = self.extract_html(url)
        return dict(re.findall("<meta .*?name=[\"'](.*?)['\"].*?content=[\"'](.*?)['\"].*?>", html))

    def crawl(self):

        while self.q:
            curr = self.q.popleft()
            curr_link = curr[0]
            curr_depth = curr[1]

            if curr_depth > 2:
                continue

            links = self.extract_links(curr_link)
            for link in links:
                if link in self.visited:
                    continue

                if 'spanish' in link:
                    continue

                if 'https://medlineplus.gov/' not in link:
                    continue

                meta = self.extract_metadata(link)
                info = f"""Link: {link}    
                                Description: {meta.get('description')}    
                                Keywords: {meta.get('keywords')}    
                                            """
                text = self.text_converter.handle(self.extract_html(link))

                print(info)
                print(curr_depth)

                file_name = 'data/' + str(self.count) + '.txt'
                output = open(file_name, 'w+')

                output.write(info)
                output.write(text)
                output.close()

                if curr_depth < 2:
                    self.q.append((link, curr_depth + 1))
                self.visited.add(link)

                print("doc count:" + str(self.count))
                self.count += 1
                # add code to save all info into local storage

    def start(self):
        self.crawl()
        # thread1 = crawl_thread(1, self.semaphore, self.q, self)
        # thread2 = crawl_thread(2, self.semaphore, self.q, self)
        # thread3 = crawl_thread(3, self.semaphore, self.q, self)
        # thread4 = crawl_thread(4, self.semaphore, self.q, self)
        #
        # thread1.start()
        # thread2.start()
        # thread3.start()
        # thread4.start()
        #
        # self.threads.append(thread1)
        # self.threads.append(thread2)
        # self.threads.append(thread3)
        # self.threads.append(thread4)
        #
        # # for t in self.threads:
        # #     t.start()
        #
        # for t in self.threads:
        #     t.join()



# class crawl_thread(threading.Thread):
#
#     def __init__(self, threadID, semaphore, q, crawler):
#         self.threadID = threadID
#         self.semaphore = semaphore
#         self.q = q
#         self.crawler = crawler
#         threading.Thread.__init__(self)
#
#     def run(self):
#
#         if not self.q:
#             time.sleep(30)
#
#
#         while self.q:
#             self.semaphore.acquire()
#             curr = self.q.popleft()
#             self.semaphore.release()
#             curr_link = curr[0]
#             curr_depth = curr[1]
#
#             if curr_depth >= 2:
#                 continue
#
#             links = self.crawler.extract_links(curr_link)
#             for link in links:
#                 if link in self.crawler.visited:
#                     continue
#
#                 meta = self.crawler.extract_metadata(link)
#                 info = f"""Link: {link}
#                 Description: {meta.get('description')}
#                 Keywords: {meta.get('keywords')}
#                             """
#                 text = self.crawler.text_converter.handle(self.crawler.extract_html(link))
#
#                 if 'spanish' in link:
#                     continue
#
#                 if not meta or not text or len(text) < 200 or 'https://medlineplus.gov' not in link or 'spanish' in link:
#                     continue
#
#                 print("threadID: " + str(self.threadID))
#                 print(info)
#
#                 self.semaphore.acquire()
#
#                 file_name = 'data/' + str(self.crawler.count) + '.txt'
#                 output = open(file_name, 'w+')
#
#                 output.write(link)
#                 output.write(info)
#                 output.write(text)
#                 output.close()
#
#                 if curr_depth < 2:
#                 self.q.append((link, curr_depth + 1))
#                 self.crawler.visited.add(link)
#
#                 print(self.crawler.count)
#                 self.crawler.index_to_html[self.crawler.count] = link
#                 self.crawler.index_to_summary[self.crawler.count] = info
#                 self.crawler.count += 1
#
#                 self.semaphore.release()
#                 # add code to save all info into local storage



if __name__ == "__main__":
    # crawler = Crawler("https://medlineplus.gov/healthtopics.html")
    # crawler.start()
    search_engine = Query.Query("./data")

    results = search_engine.query('fever weakness pain fatigue bleeding')
    # results = search_engine.query('trouble paying attention overly active')
    for result in results:
        print(result)





