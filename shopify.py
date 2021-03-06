import requests, json, time, re, random, os, pandas as pd
from dotenv import dotenv_values, load_dotenv
import urllib.parse as urlparse
from urllib.parse import parse_qs
load_dotenv()

class Shopify:

    def __init__(self,version='uk'):
        self.headers = {
            'Content-Type': 'application/json',
            'limit': "250"
        }
        self.version = version
        self.api_password = None
        self.shopify_domain = None
        self.api_version = None
        self.base_url = None
        self.api_key = None

        self.create_auth()

    def create_auth(self):
        self.api_key = os.getenv('SHOPIFY_API_KEY') if self.version == 'UK' else os.getenv('SHOPIFY_EU_API_KEY')
        self.api_password = os.getenv('SHOPIFY_API_PW') if self.version == 'UK' else os.getenv('SHOPIFY_EU_API_PW')
        self.shopify_domain = os.getenv('SHOPIFY_DOMAIN') if self.version == 'UK' else os.getenv('SHOPIFY_EU_DOMAIN')
        self.api_version = '2021-04'
        self.base_url = f"https://{self.api_key}:{self.api_password}@{self.shopify_domain}.myshopify.com/admin/api/{self.api_version}/"

    def update_page(self,data):
        api_endpoint = f"pages/{data['id']}.json"          
        payload = {
            "page": {
                "id": data['id'],
                "body_html": data['body_html']
            }
        }
        r = requests.put(url=self.base_url + api_endpoint, data=json.dumps(payload),headers=self.headers)
        res = r.json()

    def get_all_pages(self):
        # api_endpoint = 'pages.json'
        # r = requests.get(url=self.base_url + api_endpoint,headers=self.headers)
        # data = r.json()
        # return data
        api_endpoint = "pages.json"
        r = requests.get(url=self.base_url + api_endpoint,
                         headers=self.headers)
        data = r.json()
        pages = list()
        if not r.links:
            return r.json()['pages']
        pages.append(r.json()['pages'])
        next_url = r.links["next"]["url"]

        parsed = urlparse.urlparse(next_url)
        page_about = parse_qs(parsed.query)['page_info']
        count = 1
        while True:
            print(f"extracting orders from page {count}")
            url = self.base_url + api_endpoint +'?page_info='+page_about[0]
            r = requests.get(url=url,headers=self.headers)

            if r.status_code == 200:
                pages.append(r.json()['pages'])
            else:
                raise Exception("not rerieved")
            try:
                next_url = r.links["next"]["url"]
                parsed = urlparse.urlparse(next_url)
                page_about = parse_qs(parsed.query)['page_info']
            except:
                break
            time.sleep(1)
            count += 1

        pages = [x for x in pages for x in x]
        with open("pages_data.csv",mode="a") as file:
            pd.DataFrame(pages).to_csv('pages_data.csv')

        return pages
        
    def get_all_comments_per_blog(self):
        api_endpoint = 'comments.json'
        r = requests.get(url=self.base_url + api_endpoint,
                         headers=self.headers)
        data = r.json()
        comments = list()
        if not r.links:
            return r.json()['comments']
        comments.append(r.json()['comments'])
        next_url = r.links["next"]["url"]

        parsed = urlparse.urlparse(next_url)
        page_about = parse_qs(parsed.query)['page_info']
        count = 1
        while True:
            print(f"extracting comments from page {count}")
            url = self.base_url + api_endpoint +'?page_info='+page_about[0]
            r = requests.get(url=url,headers=self.headers)

            if r.status_code == 200:
                comments.append(r.json()['comments'])
            else:
                raise Exception("not rerieved")
            try:
                next_url = r.links["next"]["url"]
                parsed = urlparse.urlparse(next_url)
                page_about = parse_qs(parsed.query)['page_info']
            except:
                break
            count += 1
        return [x for x in comments for x in x]

    def remove_comment(self,id):
        api_endpoint = f"comments/{id}/remove.json"
        r = requests.post(url=self.base_url + api_endpoint,
                         headers=self.headers)
        time.sleep(0.2)
        print(f"Comment {id} removed: {r.status_code}")      

    def get_all_products(self):
        api_endpoint = "products.json"
        r = requests.get(url=self.base_url + api_endpoint,
                         headers=self.headers)
        data = r.json()
        products = list()
        if not r.links:
            return r.json()['products']
        products.append(r.json()['products'])
        next_url = r.links["next"]["url"]

        parsed = urlparse.urlparse(next_url)
        page_about = parse_qs(parsed.query)['page_info']
        count = 1
        while True:
            print(f"extracting orders from page {count}")
            url = self.base_url + api_endpoint +'?page_info='+page_about[0]
            r = requests.get(url=url,headers=self.headers)

            if r.status_code == 200:
                products.append(r.json()['products'])
            else:
                raise Exception("not rerieved")
            try:
                next_url = r.links["next"]["url"]
                parsed = urlparse.urlparse(next_url)
                page_about = parse_qs(parsed.query)['page_info']
            except:
                break
            time.sleep(1)
            count += 1
        return [x for x in products for x in x]

    def get_all_variants(self, product_id):
        api_endpoint = f"products/{product_id}/variants.json"
        r = requests.get(url=self.base_url + api_endpoint,
                         headers=self.headers)
        data = r.json()
        return data['variants']

    def update_variant_price(self, variant_id, new_price):
        api_endpoint = f"variants/{variant_id}.json"
        data = {
            "variant": {
                "id": int(variant_id),
                "price": new_price
            }
        }
        r = requests.put(url=self.base_url + api_endpoint,
                         data=json.dumps(data), headers=self.headers)
        return r.status_code

    def update_product_desc(self,id,desc):
        api_endpoint = f'/products/{id}.json'
        data = {
            "product": {
                "body_html": desc
            }
        }
        r = requests.put(url=self.base_url + api_endpoint,
                         data=json.dumps(data), headers=self.headers)
        r
    # https://shopify.dev/docs/admin-api/rest/reference/orders/order#index-2021-04
    def get_orders(self):
        api_endpoint = f"orders.json"
        params = {
            'status' : 'any'
        }
        orders = list()
        r = requests.get(url=self.base_url + api_endpoint,headers=self.headers,params=params)
        if not r.links:
            return r.json()['orders']
        
        next_url = r.links["next"]["url"]
        orders.append(r.json()['orders'])

        parsed = urlparse.urlparse(next_url)
        page_about = parse_qs(parsed.query)['page_info']
        count = 1
        while True:
            print(f"\t- extracting orders from page {count}")
            url = self.base_url + api_endpoint +'?page_info='+page_about[0]
            r = requests.get(url=url,headers=self.headers)

            if r.status_code == 200:
                orders.append(r.json()['orders'])
            else:
                raise Exception("not rerieved")
            try:
                next_url = r.links["next"]["url"]
                parsed = urlparse.urlparse(next_url)
                page_about = parse_qs(parsed.query)['page_info']
            except:
                break
            time.sleep(0.3)
            count += 1
        return [x for x in orders for x in x]


    def delete_order(self,sh_order_id):
        api_endpoint = f"orders/{sh_order_id}.json"
        r = requests.delete(url=self.base_url + api_endpoint,headers=self.headers)
        if r.status_code == 200:
            print(f"{sh_order_id} deleted...")
            return True
        elif r.status_code == 422:
            print("order cannot be deleted. Not allowed by Shopify ",sh_order_id )
        else:
            raise Exception("not deleted")

# products = sh.get_all_products()
# products_variants = list()
# for product in products:
#     product_variants = sh.get_all_variants(product["id"])
#     [products_variants.append(variant) for variant in product_variants]

# pd.DataFrame(products_variants).to_csv("products_variants.csv")

# new_prices = pd.read_csv('new_prices.csv', converters={i: str for i in range(0, 100)})
# for new_price in new_prices.iterrows():
#     variant_id = new_price[1]['variant_id']
#     price = new_price[1]['new_price']
#     sh.update_variant_price(variant_id,price)
