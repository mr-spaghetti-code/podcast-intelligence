import argparse
import os
import feedparser
import re
import requests
import time

from multiprocessing import cpu_count
from multiprocessing.pool import ThreadPool
from utils import (
    str2bool,
)


char_remove = [".",",","/","–","(",")"]

def get_podcast_urls(rss_feed):
    urls = []
    fns = []
    PodFeed = feedparser.parse(rss_feed)

    for entry in PodFeed.entries:
        title = entry.title
        clean_title = re.sub(r'[^a-zA-Z\d]', '_', title) + ".mp3"
        
        for link in entry["links"]:
            if link["type"] == "audio/mpeg":
                link_href = link.href
                print(clean_title)
                print(link_href)

                urls.append(link_href)
                fns.append(output_dir + "/" + clean_title)
    return zip(urls, fns)

def download_url(args):
    t0 = time.time()
    url, fn = args[0], args[1]
    try:
        r = requests.get(url)
        with open(fn, 'wb') as f:
            f.write(r.content)
        return(url, time.time() - t0)
    except Exception as e:
        print('Exception in download_url():', e)

def download_parallel(args):
    cpus = cpu_count()
    results = ThreadPool(cpus - 1).imap_unordered(download_url, args)
    for result in results:
        print('url:', result[0], 'time (s):', result[1])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("--rss_feed", type=str, help="The URL to the RSS feed of your podcast")
    parser.add_argument("--podcast_title", type=str, help="The title of your podcast")
    parser.add_argument("--download", type=str2bool, default=True, help="The title of your podcast")
    args = parser.parse_args().__dict__
    rss_feed: str = args.pop("rss_feed")
    podcast_title: str = args.pop("podcast_title")
    download: bool = args.pop("download")

    output_dir = f"{podcast_title}/mp3"

    os.makedirs(output_dir, exist_ok=True)

    inputs = get_podcast_urls(rss_feed)
    if download:
        download_parallel(inputs)


