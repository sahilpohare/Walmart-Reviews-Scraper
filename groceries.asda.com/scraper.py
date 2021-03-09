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
from tqdm import tqdm 
parser = argparse.ArgumentParser(description="ASAD Groceries SCRAPER")
parser.add_argument("-u", "--url", help="Product Url")
parser.add_argument("-o", "--output", help="Path to the output file", default="./output.csv")

args = parser.parse_args()
url = args.url

product_id = ""

if url is None:
    print(parser.print_help())
    sys.exit(1)
else : 
    host_list = url.split('://')
    host = ""

    if len(host_list) == 1:
        host = host_list[0].split('/')[0]
        url = host_list[0]
    else:
        host = host_list[1].split('/')[0]
        url = host_list[1]
    
    if not host == 'groceries.asda.com':
        print("WRONG WEBSITE")
        sys.exit()
print("Scraping ", url)

product_id = url.split('?')[0]
product_id = url.split('/')[-1]

offset = 0


generate_reviews_url = lambda product_id,offset=0: f'https://groceries.asda.com/review/reviews.json?requestorigin=gi&apiversion=5.4&passkey=92ffdz3h647mtzgbmu5vedbq&Filter=ProductId%3A{product_id}&Sort=SubmissionTime%3Adesc&Limit=100&Offset={offset}'

null_check_str = lambda x : str(x) if not x is None else ' '

def get_reviews(df=[], offset=0):
    reviews_url = generate_reviews_url(product_id,offset)
    response = requests.get(reviews_url)
    data = response.json()
    data_Fr = [[null_check_str(r["Title"]),null_check_str(r["Rating"]),null_check_str(r["ReviewText"])] for r in data["Results"]]
    total_reviews = data["TotalResults"]
    df.extend(data_Fr)

    while True:
        offset += 100
        if offset >= total_reviews:
            break

        reviews_url = generate_reviews_url(product_id,offset)
        response = requests.get(reviews_url)
        data = response.json()
        data_Fr = [[null_check_str(r["Title"]),null_check_str(r["Rating"]),null_check_str(r["ReviewText"])] for r in data["Results"]]
        df.extend(data_Fr)

    return df, total_reviews

                                     
def save_to_csv(frame: List[List], columns: List):
    with open(args.output, 'w', encoding='utf-8') as f:
        writer = csv.writer(f, lineterminator='\n')
        for i in tqdm(frame): 
            writer.writerow(i)

if __name__ == '__main__':
    try:
        df, total_reviews = get_reviews()
        print ("Total Reviews", total_reviews)
        save_to_csv(df,["Title", "Rating", "Review Text"])

        print ("done saved to", args.output)
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        raise SystemExit(e)
    except PermissionError as e:
        raise PermissionError("FILE ALREADY EXISTS")

