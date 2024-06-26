import sys
import requests

from bs4 import BeautifulSoup as bs
from urllib.request import urlopen

from src.logger import logging
from src.exception import CustomException


class FlipkartProductReviews:
    def __init__(self):
        self.base_url = "https://www.flipkart.com/search?q="

    def get_product_page_links(self, search_item: str) -> list:
        try:
            logging.info(f">>> fetching all product page links for {search_item} from flipkart.com")

            query_url = self.base_url + search_item
            logging.info(f"query_url: {query_url}")

            logging.info(f"Getting html object for {query_url}")
            urlclient = urlopen(query_url)
            product_page = urlclient.read()
            product_page_html = bs(product_page , 'html.parser')
            logging.info(f"html object ready for {query_url}")

            logging.info(f"Getting all product boxes")
            product_boxes = product_page_html.find_all("div" ,{"class":"cPHDOP col-12-12"})
            product_boxes = product_boxes[2:]
            logging.info(f"Found {len(product_boxes)} product boxes!")

            logging.info(f">> getting list of all product page urls")
            product_page_links = []
            for box_number, product_box in enumerate(product_boxes):
                try:
                    logging.info(f"Getting product page link for box-{box_number}")
                    product_page_link = "https://www.flipkart.com" + product_box.div.div.div.a['href']
                    logging.info(f"link found from box-{box_number}: {product_page_link}")
                    product_page_links.append(product_page_link)
                except Exception as e:
                    logging.error(f"failed to get product page link for box-{box_number}")
                    pass
            logging.info(f">> completed fetching all product page urls")

            logging.info(f">>> fetched all product page links for {search_item} from flipkart.com!")
            return product_page_links
        
        except Exception as e:
            logging.error(f">>> failed to get product page links for {search_item} from flipkart.com!")
            raise CustomException(e, sys)

    def get_review_details(self, search_item,  number_of_reviews: int) -> dict:
        try:
            product_page_links = self.get_product_page_links(search_item)

            logging.info(f">>>> getting product reviews for all links")

            reviews_from_all_pages = []
            for page_no, productlink in enumerate(product_page_links):
                logging.info(f">>> Getting html object for {page_no}, link - {productlink}")

                product_req = urlopen(productlink)
                product_html = bs(product_req, 'html.parser')

                logging.info(f"Getting all comment boxes")
                comment_boxes = product_html.find_all("div",{"class":"RcXBOT"})
                logging.info(f"found {len(comment_boxes)} comment box on this link")
                
                logging.info(f">> fetching review details from all comments boxes")
                allreviews = []
                for comment_box_number, comment_box in enumerate(comment_boxes):
                    try:
                        reviews = {"product": search_item}

                        logging.info(f"Getting reviewe details from box-{comment_box_number}")
                        reviewer = comment_box.div.div.find_all("p",{"class":"_2NsDsF AwS1CA"})[0].text
                        rating = comment_box.div.div.div.div.text
                        review_title = comment_box.div.div.div.p.text
                        review_text = comment_box.div.div.find_all("div",{"class":""})[0].text

                        review_text = review_text.replace("READ MORE", "")
                        logging.info(f"Found review details from box-{comment_box_number}")

                        reviews['reviewer'] = reviewer
                        reviews['rating'] = rating
                        reviews['review_title'] = review_title
                        reviews['review_text'] = review_text

                        allreviews.append(reviews)

                    except Exception as e:
                        logging.error(f"failed to get review details for box-{comment_box_number}")
                        pass
                
                logging.info(">> fetched review details from all correct prouct boxes!")
                
                logging.info(f">>> got all correct product reviews from page-{page_no}, link: {productlink}!")

                reviews_from_all_pages.extend(allreviews)
            
            logging.info(">>>> got product reviews for all links!")
                         
            final_reviews = reviews_from_all_pages[:number_of_reviews]
            logging.info(f"found {len(reviews_from_all_pages)} in total, user requested {number_of_reviews} reviews,  available reviews = {len(final_reviews)}. Returning {len(final_reviews)} reviews!")

            for idx, review_dict in enumerate(final_reviews):
                review_dict = {"S.No": idx+1, **review_dict}
                final_reviews[idx] = review_dict

            return final_reviews

        except Exception as e:
            logging.error(f">>>> error occured while getting review details!")
            raise CustomException(e, sys)


if __name__ == "__main__":
    search_item = "tv"
    number_of_reviews = 50
    flipkart_review_scrapper = FlipkartProductReviews()
    reviews = flipkart_review_scrapper.get_review_details(search_item, number_of_reviews)
    
    print(len(reviews))

    
