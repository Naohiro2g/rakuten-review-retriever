# output: rakuten_review.csv
# format: score, date, comment

import requests
import lxml.html
import pandas as pd
import time
import sys
from itertools import count

# INPUT_URL = "https://review.rakuten.co.jp/item/1/330517_10002841/1.1/"  # 10 pages
# INPUT_URL = "https://review.rakuten.co.jp/item/1/330517_10002630/1.1/"  # one page
INPUT_URL = "https://review.rakuten.co.jp/item/1/330517_10003205/1.1/"  # 35
OUTPUT_FILE = "rakuten_review.csv"
PAGE_INTERVAL = 30


def pages(url, page_interval=PAGE_INTERVAL):
    for page in count(1):
        print()
        print(f" page {page} ".center(70, '-'))
        print("\rRetlieving reviews... ", end='')
        html = requests.get(url).text
        xml = lxml.html.fromstring(html)
        yield xml
        print("done.\r")
        # there is no link to the next page if the product item has only one page of review
        try:
            next_page = xml.find_class("revPagination")[0].xpath('a')[-1]
            #  it's done if it is the last page
            if not next_page.text.startswith('次の15件'):
                return
        except IndexError:
            return
        url = next_page.xpath('@href')[0]
        print(f"... move to the next page in {page_interval} seconds:")
        print(f"  {url}")
        time.sleep(page_interval)


# コメント内改行を"<br>"に変換"
def reviews(xmls):
    for xml in xmls:
        # reviews = xml.find_class("revRvwUserMain")
        reviews = xml.find_class("revRvwUserSec")
        for review in reviews:
            score = review.find_class("revUserRvwerNum value")[0].text
            # comment = review.find_class("revRvwUserEntryCmt description")[0].text  # only the first line
            comment = review.find_class("revRvwUserEntryCmt description")[0].text_content()  # the whole comment
            comment = comment.replace("\n", "<br>  ")
            date_reviewed = review.find_class("revUserEntryDate dtreviewed")[0].text
            # print(score, date_reviewed, comment)
            yield score, date_reviewed, comment
            # user_details = review.find_class("revUserFaceDtlTxt")[0]
            # print(user_details, user_details.text)
            # try:
            #     age, sex = age_sex.split(" ")
            # except ValueError:
            #     age = ""
            #     sex = ""
            # print(age, sex)
            # yield score, date_reviewed, comment, age, sex


def save(review_lines, file_name=OUTPUT_FILE, encoding='utf_8_sig'):
    print("\nPreparing the csv file to save...")
    # columns = ["score", "date_reviewed", "comment", "age", "sex"]
    columns = ["score", "date_reviewed", "comment"]
    df = pd.DataFrame(review_lines, columns=columns)
    df.to_csv(file_name, encoding=encoding)


def main():
    url = INPUT_URL if len(sys.argv) <= 1 else sys.argv[1]
    xmls = pages(url)
    review_lines = reviews(xmls)
    save(review_lines)


if __name__ == '__main__':
    main()
