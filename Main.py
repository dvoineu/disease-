import argparse
import Query
import time

if __name__ == '__main__':

    parser = argparse.ArgumentParser(prog="Simple_Search_Engine",
                                     description="Interactive search Engine for CDC press")
    parser.add_argument("-e", "--evaluation", action='store_true',
                        help="optional: show the formal evaluation of the search engine")

    # print(parser.parse_args(["-s", "fooo/nar/stopword.txt", "-d", "dir/path/to/folder"]))

    args = parser.parse_args()
    if args.evaluation:
        Query.formal_evaluation()
        exit(0)

    search_engine = Query.Query("./cdcs")
    while True:
        print("enter query below, or enter \"QUIT555\" (exact phase) to quite")
        query = input("Enter your query: ")
        if query == "QUIT555":
            exit(0)
        current_time = time.time()
        result = search_engine.query(query)
        for docs in result:
            print(search_engine.id_file[docs], docs)
            print("Search Time: " + str(time.time() - current_time))





