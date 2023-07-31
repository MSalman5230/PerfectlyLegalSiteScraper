import scrapy
import requests
from datetime import datetime
import re
from urllib.parse import urlparse, parse_qs


class mainSpider(scrapy.Spider):
    name = "LegalStuff"
    PAGE_COUNTER = 1

    # creator_id=""           #CHANGE
    def start_requests(self):
        urls = [
            "",
        ]

        for url in urls:
            self.PAGE_COUNTER = 1
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        domain = urlparse(response.url).scheme + "://" + urlparse(response.url).hostname
        for i in response.xpath("//article[@class='post-card post-card--preview']"):
            # title = i.xpath(".//div/a/img/@alt").get()

            sub_url = domain + i.xpath(".//a/@href").get()
            # print(sub_url)
            search_string = self.get_search_string_from_url(response.url)

            yield scrapy.Request(url=sub_url, callback=self.parse_item, meta={"search_string": search_string})

        # Find Next Page then pass the url to this function
        next_page = response.xpath("//a[@class='next']/@href").get()
        if next_page:
            self.PAGE_COUNTER += 1
            print(f"PARSING PAGE {self.PAGE_COUNTER}")
            next_page = domain + next_page
            yield scrapy.Request(url=next_page, callback=self.parse)

    def parse_item(self, response):
        unique_item = []
        creator_id = response.url.split("/")[-3]
        platform = response.url.split("/")[-5]
        title = response.xpath("//h1[@class='post__title']/span/text()").get()

        publishedAt = response.xpath("//div[@class='post__published']/time/@datetime").get()
        publishedAt = self.parse_published_at(publishedAt)

        text_body = self.get_item_contents(response)
        search_type = self.get_search_info(response.meta["search_string"])
        item = {
            "searchType": search_type,
            "searchTerm": response.meta["search_string"],
            "platform": platform,
            "creatorId": creator_id,
            "title": title,
            "postURL": response.url,
            "publishedAt": publishedAt,
            "scrapedAt": datetime.utcnow(),
            "textContent": text_body,
        }

        item["files"] = []
        for i in response.xpath("//li[@class='post__attachment']"):
            file_name = i.xpath(".//a/@download").get()
            file_url = i.xpath(".//a/@href").get()
            file_size = self.get_file_size(file_url)
            if file_url in unique_item:
                continue
            item["files"].append({"name": file_name, "url": file_url, "size": file_size})

            unique_item.append(file_url)

        if len(item["files"]) > 0:
            yield item

    def get_file_size(self, url):
        try:
            response = requests.head(url)
            if response.status_code == 200:
                content_length = int(response.headers.get("Content-Length", 0)) / (1024 * 1024)
                return content_length
            else:
                print(f"Failed to get file size. Status code: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return None

    def get_item_contents(self, response):
        all_text = ""
        for i in response.xpath("//div[@class='post__content']/p"):
            # print(i)
            text = i.xpath(".//text()").get()

            if text == None:
                continue

            text = re.sub(r"\s+", " ", text)
            all_text = all_text + text + "\n"

        for i in response.xpath("//div[@class='post__content']/pre"):
            # print(i)
            text = i.xpath(".//text()").get()
            if text == None:
                continue
            text = re.sub(r"\s+", " ", text)

            all_text = all_text + text + "\n"

        return all_text

    def get_search_string_from_url(self, url):
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        search_string = query_params.get("q", [None])[0]
        return search_string

    def get_search_info(self, search_string):
        search_type = ""
        if search_string == None:
            search_type = "creator"

        else:
            search_type = "string"

        return search_type

    def parse_published_at(self, published_at):
        try:
            # Try parsing without seconds  format

            return datetime.strptime(published_at, "%Y-%m-%d %H:%M:%S")

        except ValueError:
            try:
                # If parsing without seconds format fails, try parsing without microseconds
                return datetime.strptime(published_at, "%Y-%m-%d %H:%M:%S.%f")

            except ValueError:
                # If parsing both formats fails, handle the error here
                return None
