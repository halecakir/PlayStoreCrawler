# Play Store Crawler

Yet another Scrapy and Selenium based Google Play store crawler.

# New Features!
  - List featured apps by category.
  - Crawl similar apps.
  - Add more app info e.g. sizes, installs, permission.

### Installation

PlayStoreCrawler requires headless [Chrome](https://www.google.com/chrome/) v59+ to run.

Install the dependencies.

```sh
$ pip3 install -r requirements.txt
```

### Usage

Crawl featured apps from Play Store.

```sh
$ scrapy crawl featured-apps-spider -o ../data/featured_apps.csv --set JOBDIR=crawl
```

Below script extracts detailed app information, then repeats this process for each of its similar apps. This script requires inital app list. You can prepare initial app list with ```featured-apps-spider```.

```sh
$ scrapy crawl similar-apps-spider -o ../data/apps.csv --set JOBDIR=crawl_similar
```

### Todos
    





