'''
********************************************************************************************
 * Copyright (C) 2021 Sahil Pohare (Email: sahilpohare@gmail.com, Github: @sahilpohare)    |
 *                                                                                         |     
 * This file is part of Walmart.Com Reviews Scraper .                                   |
 *                                                                                         |             
 * Walmart.com Reviews Scraper can not be copied and/or distributed without the express |
 * permission of Sahil Pohare                                                              |
 *******************************************************************************************
'''
import argparse
import sys
from typing import List
from bs4 import BeautifulSoup
from bs4.element import PageElement
import requests
import csv
import os

def cls():
    os.system('cls' if os.name=='nt' else 'clear')

parser = argparse.ArgumentParser(description="Walmart.Com Review Scraper")
parser.add_argument("-u", "--url", help="Product Url")
parser.add_argument(
    "-o", "--output", help="Path to the output file", default="./output.csv"
)

args = parser.parse_args()
url = args.url

product_id: str

if url is None:
    print(parser.print_help())
    sys.exit(1)
else:
    host_list = url.split("://")
    host = ""

    if len(host_list) == 1:
        host = host_list[0].split("/")[0]
        url = host_list[0]
    else:
        host = host_list[1].split("/")[0].split('.')
        url = host_list[1]

    if not host == 'www.walmart.com':
        print("WRONG WEBSITE")
        sys.exit()
print("Scraping ", url)

product_id = url.split("?")[0]
product_id = url.split("/")[-1]

generate_reviews_url = (
    lambda product_id, page_no=1: f"https://www.walmart.com/reviews/product/{product_id}?page={page_no}"
)
null_check_str = lambda x: str(x) if not x is None else " "


def null_check_func(x, placeholder):
    try:
        if x:
            return x.get_text()
        else:
            return placeholder
    except:
        return placeholder


class Review:
    title: str
    review_text: str
    rating: int
    date: str

    def __init__(self, review_block: PageElement):
        self.title = null_check_func(
            review_block.find(class_="review-title"), "No Title"
        )
        self.username = null_check_func(
            review_block.find(class_="review-footer-userNickname"), "WalmartUser"
        )
        self.review_text = (
            review_block.find(class_="review-text").p.get_text()
            if hasattr(review_block.find(class_="review-text"), "p")
            else "No Review Text"
        )
        self.rating = float(
            null_check_func(review_block.find(class_="seo-avg-rating"), 0)
        )
        self.date = review_block.find(class_="review-date-submissionTime").get_text()

    def get_list(self):
        return [self.title, self.username, self.date, self.rating, self.review_text]

    @staticmethod
    def get_fields():
        return ["Title", "Username", "Date", "Rating (x out of 5)", "Review_Text"]

    def __str__(self):
        return f"Review(user: {self.username}, title : {self.title}, date : {self.date}, review_text : {self.review_text}, rating : {self.rating})"


def save_to_csv(frame: List[List], writingmode = 'w'):
    with open(args.output, writingmode, encoding="utf-8") as f:
        writer = csv.writer(f, lineterminator="\n")
        for i in frame:
            writer.writerow(i)


def get_reviews():
    df = []
    parser = "html.parser"
    reviews_url = generate_reviews_url(product_id, 1)
    response = requests.get(reviews_url)

    soup = BeautifulSoup(response.content, parser)

    pages = int(list(soup.find(class_="paginator-list").children)[-1].get_text())

    for i in range(pages):
        
        #Animation Code
        cls()
        outp = ['-'] * pages
        outp.insert(0, '[')
        outp.append(']')
        p = '{percent:.2%}'.format(percent=(i+1)/pages)
        outp[i] = f"{p} ===>"
        print('Scraping', args.url)
        print(''.join(outp), f"page {i + 1} of {pages}")
        #Animation Code End

        reviews_url = generate_reviews_url(product_id, i + 1)
        response = requests.get(reviews_url)

        soup = BeautifulSoup(response.content, parser)

        review_wraper_list = soup.find_all(class_="Grid ReviewList-content")
        pages = int(list(soup.find(class_="paginator-list").children)[-1].get_text())

        df.extend([Review(i).get_list() for i in review_wraper_list])

    return df, pages


if __name__ == "__main__":
    try:
        save_to_csv([Review.get_fields()])
        df, pages = get_reviews()
        print("Total Pages", pages)
        save_to_csv(df, 'a+')

        print("done saved to", args.output)

    except requests.exceptions.RequestException as e:  # This is the correct syntax
        raise SystemExit(e)
    except PermissionError as e:
        raise PermissionError("FILE ALREADY EXISTS")
