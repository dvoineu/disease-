import argparse
import Query
import crawler
import time
import subprocess

if __name__ == '__main__':

    parser = argparse.ArgumentParser(prog="Disease_Search_Engine",
                                     description="Interactive search Engine for contents in cdc.gov")
    parser.add_argument("-c", "--crawl", action='store_true',
                        help="optional: crawl the content from cdc again. Warning: it will take a lot of time")
    parser.add_argument("-i", "--index", action='store_true',
                        help="optional: index the content from local file again. Warning: it will take a lot of time")

    # print(parser.parse_args(["-s", "fooo/nar/stopword.txt", "-d", "dir/path/to/folder"]))

    args = parser.parse_args()
    if args.crawl:
        crawler = crawler.Crawler("https://www.cdc.gov/DiseasesConditions/")
        crawler.start()

    search_engine = Query.Query("./data", not args.index)

    while True:
        print("enter query below, or enter \"QUIT555\" (exact phase) to quite")
        query = input("Enter your query: ")
        if query == "QUIT555":
            exit(0)
        current_time = time.time()
        result = search_engine.query(query)
        for docs in result:
            print(docs)
            print("Search Time: " + str(time.time() - current_time))
            print('opening result document:')
            doc = './data/' + str(docs) + '.txt'
            subprocess.run(['open', doc], check=True)





