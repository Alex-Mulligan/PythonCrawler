from threading import Thread

from utils.download import download
from utils import get_logger
from scraper import scraper
import time, simhash #simhash from https://github.com/leonsim/simhash


class Worker(Thread):
    def __init__(self, worker_id, config, frontier, report):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
        self.report = report
        super().__init__(daemon=True)
        
    def run(self):
        while True:
            tbd_url = self.frontier.get_tbd_url()
            if not tbd_url:
                self.logger.info("Frontier is empty. Stopping Crawler.")
                self.frontier.end_thread()
                if self.frontier.threadCount == 0:
                    self.report.print_report()
                break
            resp = download(tbd_url, self.config, self.logger)
            self.logger.info(
                f"Downloaded {tbd_url}, status <{resp.status}>, "
                f"using cache {self.config.cache_server}.")
            scraped_urls, tokens = scraper(tbd_url, resp)
            #checks to make sure page is not empty and not a duplicate (using simhash)
            if not tokens == '' and not self.frontier.simhashIndex.get_near_dups(simhash.Simhash(tokens)):
                self.report.store_report(tbd_url, tokens)
                self.frontier.add_simhash(tbd_url, tokens)
                for scraped_url in scraped_urls:
                    self.frontier.add_url(scraped_url)
            self.frontier.mark_url_complete(tbd_url)
#             time.sleep(self.config.time_delay)
