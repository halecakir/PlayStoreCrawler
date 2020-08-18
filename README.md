# Play Store Crawler

Yet another Scrapy and Selenium based Google Play store crawler.

# New Features!
  - List featured apps by category.

### Installation

PlayStoreCrawler requires headless [Chrome](https://www.google.com/chrome/) v59+ to run.

Install the dependencies.

```sh
$ pip3 install -r requirements.txt
```

### Usage

Crawl featured apps.

```sh
$ scrapy crawl featured-apps-spider -o ../data/featured_apps.csv --set JOBDIR=crawl
```

### Todos

 - Crawl similar apps.
 - Add more app info e.g. sizes, installs, permission.





