
'''
********************************************************************************************
 * Copyright (C) 2021 Sahil Pohare (Email: sahilpohare@gmail.com, Github: @sahilpohare)    |
 *                                                                                         |     
 * This file is part of Walmart Canada Reviews Scraper .                                   |
 *                                                                                         |             
 * Walmart Canada Reviews Scraper can not be copied and/or distributed without the express |
 * permission of Sahil Pohare                                                              |
 *******************************************************************************************
'''

from typing import List
import requests
import argparse
import csv
import os
import sys

# Utilities
def cls():
    os.system('cls' if os.name=='nt' else 'clear')

null_check_str = lambda x, default_=" ": str(x) if not x is None else default_
# Utilities End

parser = argparse.ArgumentParser(description="Walmart Canada Reviews Scraper")
parser.add_argument("-u", "--url", help="Product Url")
parser.add_argument(
    "-o", "--output", help="Path to the output file", default="./output.csv"
)

args = parser.parse_args()
url = args.url

product_id = ""

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
        host = host_list[1].split("/")[0]
        url = host_list[1]

    if not host == "www.walmart.ca":
        print("WRONG WEBSITE")
        sys.exit()
        
print("Scraping ", url)

product_id = url.split("?")[0]
product_id = product_id.split("/")[-1]

print('PRODUCTID',product_id)

offset = 0


generate_reviews_url = (
    lambda product_id, offset=0: f"https://api.bazaarvoice.com/data/reviews.json?apiversion=5.5&passkey=e6wzzmz844l2kk3v6v7igfl6i&Filter=ProductId:{product_id}&Sort=Rating:desc&Limit=100&Offset={offset}"
)


def get_reviews(df=[], offset=0):
    reviews_url = generate_reviews_url(product_id, offset)
    response = requests.get(reviews_url)
    data = response.json()
    data_Fr = [
        [
            null_check_str(r["UserNickname"]),
            null_check_str(r["AuthorId"]),
            null_check_str(r["Id"]),
            null_check_str(r["SubmissionTime"]),
            null_check_str(r["ModerationStatus"]),
            null_check_str(r["Title"], "No Title"),
            null_check_str(r["Rating"]),
            null_check_str(r["ReviewText"], "No Review Text"),
        ]
        for r in data["Results"]
    ]
    total_reviews = data["TotalResults"]

    if(total_reviews == 0):
        raise ValueError("NO REVIEWS FOUND FOR PRODUCT")

    print(reviews_url)
    df.extend(data_Fr)

    while True:
        offset += 100

        #Animation Code
        cls()
        outp = ['-'] * offset
        outp.insert(0, '[')
        outp.append(']')
        p = '{percent:.2%}'.format(percent=(min(offset,total_reviews))/total_reviews)
        outp[offset] = f"{p} ===>"
        print('Scraping', args.url)
        print(''.join(outp), f"Reviews Scraped {min(offset,total_reviews)} of {total_reviews}")
        #Animation Code End

        if offset >= total_reviews:
            break

        reviews_url = generate_reviews_url(product_id, offset)
        response = requests.get(reviews_url)
        data = response.json()
        data_Fr = [
            [
                null_check_str(r["UserNickname"]),
                null_check_str(r["AuthorId"]),
                null_check_str(r["Id"]),
                null_check_str(r["SubmissionTime"]),
                null_check_str(r["ModerationStatus"]),
                null_check_str(r["Title"], "No Title"),
                null_check_str(r["Rating"]),
                null_check_str(r["ReviewText"], "No Review Text"),
            ]
            for r in data["Results"]
        ]
        df.extend(data_Fr)

    return df, total_reviews


def save_to_csv(frame: List[List], columns: List):
    with open(args.output, "w", encoding="utf-8") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(columns)
        for i in frame:
            writer.writerow(i)


if __name__ == "__main__":
    try:
        df, total_reviews = get_reviews()
        print("Total Reviews", total_reviews)
        save_to_csv(df, ["Username", "UserId", "ReviewID", "Submission Time","ModerationStatus", "Title", "Rating", "Review Text"])

        print("done saved to", args.output)
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        raise SystemExit(e)
    except PermissionError as e:
        raise PermissionError("FILE ALREADY EXISTS")
