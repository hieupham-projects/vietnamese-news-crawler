import argparse
import json
from multiprocessing import Pool

from tqdm import tqdm

from crawler.crawler_arguments import CrawlerArguments
from crawler.crawler_factory import CrawlerFactory

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--start-range", type=str, required=True)
    parser.add_argument("--end-range", type=str, required=True)
    parser.add_argument("--category", type=str, required=True)
    parser.add_argument("--crawler-type", type=str, required=True)
    parser.add_argument("--num-processes", type=int, required=True)
    parser.add_argument("--output-file-path", type=str, required=True)
    args = parser.parse_args()

    crawler_arguments = CrawlerArguments(
        start_range=args.start_range, end_range=args.end_range, category=args.category
    )
    crawler = CrawlerFactory.create_crawler(
        crawler_type=args.crawler_type, arguments=crawler_arguments
    )

    urls = crawler.crawl_urls()

    with Pool(args.num_processes) as pool:
        results_iter = list(
            tqdm(pool.imap(crawler.crawl_articles, urls), total=len(urls))
        )

    articles = [content for content in results_iter if content]
    # Dump the list of objects to a JSON file
    with open(args.output_file_path, "w", encoding="utf-8") as json_file:
        json.dump(articles, json_file, ensure_ascii=False, indent=4)
