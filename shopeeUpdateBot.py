import re
import time
from pprint import pprint
import datetime

import pyshopee
from pyshopee import Client


def _builder_attributes(attributes_resp, brand_option=None, default_brand_option="No Brand"):
    attributes = []
    #유통기한 어트리뷰트 때문에 변수 미리지정 _ 유통기한은 지금으로부터 1년으로 전부 지정!
    now = datetime.datetime.now()
    Best_Before = now + datetime.timedelta(days=365)
    Best_Before = time.mktime(Best_Before.timetuple())
    # in case attributes response is not define in api response
    if attributes_resp.get("attributes"):
        for ele in attributes_resp.get("attributes"):
            if ele.get("is_mandatory") and ele.get("attribute_name") == '品牌':
                attributes.append(
                    {
                        "attributes_id": ele.get("attribute_id"),
                        "value": brand_option if brand_option else default_brand_option
                    })
            elif ele.get("is_mandatory") and ele.get("attribute_id") == 10839: #Best_Before 섭취 추천일 필수일경우!
                attributes.append(
                    {
                        "attributes_id": ele.get("attribute_id"),
                        "value": str(int(Best_Before))
                    })
            elif ele.get("is_mandatory"):
                attributes.append(
                    {
                        # checking the value if value can radom or set as " "
                        "attributes_id": ele.get("attribute_id"),
                        "value": ele.get("options")[0] if len(ele.get("options")) > 0 else " ",
                    })
            else:
                pass
    else:
        return None
    return attributes


def _builder_logistics(**params):
    logistics = list()

    resp = shopee.logistic.get_logistics()

    logistics_resp = resp.get("logistics")
    for logis in logistics_resp:
        if logis.get('enabled'):
            # logistics.append({
            #     'logistic_id': logis.get('logistic_id'),
            #     'enabled': logis.get('enabled')
            # })
            if logis.get('fee_type') == 'SIZE_SELECTION':
                logis['sizes'] = logis['sizes'][0]['size_id']
            else:
                logistics.append(logis)

    return logistics


def _builder_images(images, **params):
    data = []
    for image in images:
        data.append({'url': image})

    return data


def _builder_variations(data, **params):
    multi = len(data) if len(data) > 1 else None

    variations_container = []
    if multi:
        for ele in data:

            variations = {}

            # check
            if ele["modelid"] == 0 or ele["model_status"] == 0:
                pass
            else:
                variations.setdefault("name", ele["model_name"].strip())
                variations.setdefault("stock", 1)
                variations.setdefault("price", ele["model_price"])
                if ele.get("variation_sku"):
                    variations.setdefault("variation_sku", ele.get("variation_sku"))

                variations_container.append(variations)
        return variations_container

    else:
        return None


def _builder_weight(single, default_weight=0.1, **params):
    ''' the net weight of this item, the unit is KG.
    - type: float
    - require: yes
    '''
    if single.get("item_weight"):
        weight = single.get("item_weight") / 100000
    else:
        weight = default_weight

    return float(weight)


def _cleaning_hashtag(description, **params):
    hashtag_pattern = re.compile(r"#(.*)[\s]{0,1}", flags=re.UNICODE)
    cleaned_description = hashtag_pattern.sub(r' ', description)

    return cleaned_description


def add_item(shopee, category_id, item_name, description, images, item_price, item_weight, stock, item_sku):
    product_data = {
        "category_id": category_id,
        "name": item_name,
        "description": _cleaning_hashtag(description=description),
        "price": item_price,
        "stock": stock,
        "weight": item_weight,
        "images": _builder_images(images),
        "logistics": _builder_logistics(),
        'item_sku': item_sku,
        'partner_id': shopee.partner_id,
        'shopid': shopee.shop_id,
        'timestamp': int(time.time()),
        "attributes": _builder_attributes(
            attributes_resp=shopee.item.get_attributes(category_id=category_id),
            brand_option=None,
            default_brand_option="No Brand"),
    }
    # adding process
    response = shopee.item.add(product_data=product_data)
    print(response)


def update_item(shopee, item_id, category_id, item_name, description, images, item_price, item_weight, stock, item_sku):
    product_data = {
        'item_id': item_id,
        "category_id": category_id,
        "name": item_name,
        "description": _cleaning_hashtag(description=description),  ## SEX
        "price": item_price,
        "stock": stock,
        "weight": item_weight,
        "images": _builder_images(images),
        "logistics": _builder_logistics(),
        'partner_id': shopee.partner_id,
        'shopid': shopee.shop_id,
        'timestamp': int(time.time()),
        'item_sku': item_sku,
        "attributes": _builder_attributes(
            attributes_resp=shopee.item.get_attributes(category_id=category_id),
            brand_option=None,
            default_brand_option="No Brand"),
    }
    # adding process
    response = shopee.item.update_item(update_data=product_data)
    print(response)

def update_item_price(shopee, item_id, item_price):
    product_data = {
        "price": item_price,
        'partner_id': shopee.partner_id,
        'shopid': shopee.shop_id,
        'timestamp': int(time.time()),
    }
    # adding process
    response = shopee.item.update_price(item_id=item_id,update_data=product_data)
    print(response)

def update_item_image(shopee, item_id, images):
    product_data = {
        'item_id': item_id,
        "category_id": category_id,
        "name": item_name,
        "description": _cleaning_hashtag(description=description),
        "price": item_price,
        "stock": stock,
        "weight": item_weight,
        "images": _builder_images(images),
        "logistics": _builder_logistics(),
        'partner_id': shopee.partner_id,
        'shopid': shopee.shop_id,
        'timestamp': int(time.time()),
        'item_sku': item_sku,
        "attributes": _builder_attributes(
            attributes_resp=shopee.item.get_attributes(category_id=category_id),
            brand_option=None,
            default_brand_option="No Brand"),
    }
    # adding process
    response = shopee.item.update_item(update_data=product_data)
    print(response)

# Shop_id_dict
shop_id_list = {}
shop_id_list['sg'] = 193062841
shop_id_list['ph'] = 272109011

if __name__ == '__main__':
    shopid = shop_id_list['ph']  # shop_id_list에서 추출
    partner_id = 845757  # Shopee Open Platform에서 제공해준 파트너 아이디
    API_key = '365d808e251713654d3300ad88ecde1461f75cec50b54b9b54e44f99adf7dcc2'
    shopee: Client = pyshopee.Client(shop_id=shopid,
                             partner_id=partner_id,
                             secret_key=API_key)
#-----------------------------------------------------------------------------------------------------------------------
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import requests

#구글API설정
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name('Tako translate-e60ac1cd9c41.json', scope)

#["#0 과자-로켓와우","#1 뷰티-스킨케어-로켓와우","#2 커피믹스-로켓","#3시리얼-로켓와우","#4뷰티-클렌징/필링-로켓와우","#5식품-건강식품-로켓","#6뷰티-선물세트/키트","#7식품-과자/초콜릿/시리얼-과자-로켓와우"]
#다수의 스프레스 시트 업로드
Target_sheet_list = ["필리핀PH"]

#구글 스프레드시트 지정
gc = gspread.authorize(credentials)
for Target_sheet in Target_sheet_list:
    ws = gc.open("국가별SKU-ItemID매칭시트").worksheet(Target_sheet)

    # Setting the list
    item_id_list = ws.col_values(2)
    item_price_list = ws.col_values(3)

    # list에서 data 가져와서 for문 돌면서 update_price 실행
    start_row = 3 #start point
    start_row -= 1
    while start_row <= len(item_id_list) - 1:
        # update_price 실행
        response = shopee.item.update_price(item_id=int(item_id_list[start_row]),
                                            price=float(item_price_list[start_row]),
                                            partner_id=shopee.partner_id,
                                            shopid=shopee.shop_id,
                                            timestamp=int(time.time()),)
        print(response)
        # 현재 진행중
        print(f'{start_row + 1} row updated')
        start_row += 1
    print(Target_sheet+'sheet uploaded')

    time.sleep(5)
