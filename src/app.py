from flask import Flask, render_template, request, jsonify
import requests
from requests.exceptions import RequestException
from tf2_utils import Inventory, map_inventory, Item
from tf2_utils.schema import SchemaItemsUtils
from sku.parser import Sku
import re
import pickle
import os

app = Flask(__name__)


@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"Server Error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(Exception)
def handle_unexpected_error(error):
    app.logger.error(f"Unexpected Error: {error}")
    return jsonify({'error': 'An unexpected error occurred'}), 500

def get_item_list():
    if "src" in os.getcwd():
        data_path = "../data/item_list.pkl"
    else:
        data_path = "./data/item_list.pkl"


    with open(data_path, "rb") as fp:
        item_list = pickle.load(fp)

    return item_list

def get_inventory_list(profile_url, api_key):
    try:
        steamid64 = get_steam_id64(profile_url)
        if not steamid64:
            raise ValueError("Invalid Steam profile URL or unable to fetch SteamID64.")

        provider = Inventory("steamcommunity", api_key)
        user_inventory = provider.fetch(steamid64)

        if not user_inventory:
            raise ValueError("Failed to fetch user inventory. Make sure your inventory is public!")

        mapped_inventory = map_inventory(user_inventory, add_skus=True)
        return mapped_inventory

    except ValueError as e:
        app.logger.error(f"ValueError in get_inventory_list: {e}")
        return jsonify({'error': str(e)}), 400

    except requests.exceptions.RequestException as e:
        app.logger.error(f"Network error in get_inventory_list: {e}")
        return jsonify({'error': 'Network error while fetching data from Steam.'}), 500

    except KeyError as e:
        app.logger.error(f"Missing data in get_inventory_list: {e}")
        return jsonify({'error': 'Unexpected data format in the inventory.'}), 500

    except Exception as e:
        app.logger.error(f"Unexpected error in get_inventory_list: {e}")
        return jsonify({'error': 'An unexpected error occurred while fetching inventory data.'}), 500



def get_detailed_info(mapped_inventory, item_list,  ignore_tradable, ignore_qualities):

    halloween_items = {}
    halloween_data = {}

    for item in mapped_inventory:

        if ignore_tradable:
            if item["tradable"] == 1:
                continue

        if ignore_qualities:
            if Item(item).get_quality() != "Unique":
                continue

        for master in item_list:
            if normalize_name(clean_item_name(item["name"])).lower() == master.lower():
                halloween_items[master.lower()] = + 1
                if master.lower() not in halloween_data:
                    halloween_data[master.lower()] = [item]
                else:
                    halloween_data[master.lower()].append(item)

    return halloween_items, halloween_data

def normalize_name(name):
    return name.replace("The ", "").strip()


def clean_item_name(item_name: str) -> str:
    modifiers = [
        "Genuine", "Haunted", "Strange", "Unusual", "Collector's", "Vintage", "Community", "Community", "Decorated",
        "Self-Made", "Pro", "Uncraftable", "Manndatory", "Professional", "Festive", "Botkiller", "Souvenir",
        "Team Captain"
    ]

    # could be improved
    while True:
        for modifier in modifiers:
            if item_name.startswith(modifier + " "):
                item_name = item_name[len(modifier) + 1:].strip()
                break
        else:
            break

    return item_name


def get_steam_id64(profile_url):

    try:
        if "/id/" in profile_url:
            response = requests.get(profile_url)
            response.raise_for_status()  # Raise an exception for HTTP errors
            match = re.search(r'"steamid":"(\d+)"', response.text)
            if match:
                return match.group(1)
            else:
                raise ValueError("Could not find SteamID64 in the profile page.")

        elif "/profiles/" in profile_url:
            match = re.search(r"steamcommunity.com/profiles/(\d+)", profile_url)
            if match:
                return match.group(1)
            else:
                raise ValueError("Invalid Steam profile URL format.")

        else:
            raise ValueError("Invalid Steam profile URL format.")

    except ValueError as e:
        print(f"Error: {e}")
        return None

    except RequestException as e:
        print(f"Network error while fetching profile URL: {e}")
        return None


def get_halloween_data(api_key, profile_url, ignore_tradable, ignore_qualities):

    try:
        mapped_inventory = get_inventory_list(profile_url, api_key)

        item_list = get_item_list()

        halloween_items, halloween_data = get_detailed_info(mapped_inventory, item_list, ignore_tradable, ignore_qualities)

        missing_items = []

        for item in item_list:
            if item.lower() not in halloween_items.keys():
                missing_items.append(item)

        items_and_images = []
        sku = Sku()  # we are using this since the tf2_utils one is supposedly not accurate
        schema = SchemaItemsUtils()

        for item in missing_items:

            try:
                item_sku = sku.name_to_sku(item)
                url = schema.sku_to_image_url(item_sku)
            except:
                url = None
            items_and_images.append((item, url))


        return items_and_images
    except ValueError as e:
        print(f"ValueError in get_halloween_data: {e}")
        return jsonify({'error': str(e)}), 400

    except Exception as e:
        print(f"Unexpected error in get_halloween_data: {e}")
        return jsonify({'error': 'An unexpected error occurred while processing the Halloween data.'}), 500



def get_repeated_items(api_key, profile_url, ignore_tradable, ignore_qualities):
    try:
        mapped_inventory = get_inventory_list(profile_url, api_key)


        item_list = get_item_list()

        halloween_items, halloween_data = get_detailed_info(mapped_inventory, item_list, ignore_tradable, ignore_qualities)
        repeated_items = []

        for k in halloween_data.keys():
            ln = len(halloween_data[k])
            if ln > 1:
                repeated_items.append((halloween_data[k][0]["name"], len(halloween_data[k]), halloween_data[k][0]["actions"][0]["link"] ))

        items_and_images = []
        sku = Sku()  # we are using this since the tf2_utils one is supposedly not accurate
        schema = SchemaItemsUtils()

        for item in repeated_items:

            try:
                url = schema.sku_to_image_url(sku.name_to_sku(item[0]))
            except:
                url = None

            #get tf2 wiki links - some do not work, look later!
            #items_and_images.append((item[0], url, item[1], item[2]))
            items_and_images.append((item[0], url, item[1]))


        return items_and_images

    except ValueError as e:
        print(f"ValueError in get_halloween_data: {e}")
        return jsonify({'error': str(e)}), 400

    except Exception as e:
        print(f"Unexpected error in get_halloween_data: {e}")
        return jsonify({'error': 'An unexpected error occurred while processing the Halloween data.'}), 500

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/get_halloween_data', methods=['POST'])
def fetch_halloween_data():
    api_key = request.form.get('api_key')
    profile_url = request.form.get('profile_url')


    ignore_tradable = request.form.get('ignore_tradable', 'false') == 'true'  # or 'on' for checked
    ignore_qualities = request.form.get('ignore_qualities', 'false') == 'true'

    if not api_key:
        return jsonify({'error': 'API key is required'}), 400

    if not profile_url:
        return jsonify({'error': 'Profile URL is required'}), 400

    try:
        data = get_halloween_data(api_key, profile_url, ignore_tradable, ignore_qualities)
        return jsonify(data)

    except ValueError as e:
        print(e)
        return jsonify({'error': str(e)}), 400

    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({'error': 'An unexpected error occurred while processing the request.'}), 500


@app.route('/get_repeated_data', methods=['POST'])
def get_repeated_data():
    api_key = request.form.get('api_key')
    profile_url = request.form.get('profile_url')


    ignore_tradable = request.form.get('ignore_tradable', 'false') == 'true'
    ignore_qualities = request.form.get('ignore_qualities', 'false') == 'true'

    if not api_key or not profile_url:
        return jsonify({'error': 'API key and profile URL are required'}), 400

    data = get_repeated_items(api_key, profile_url, ignore_tradable, ignore_qualities)

    return jsonify(data)

if __name__ == '__main__':
    #app.run(debug=True)
    if "/app" in os.getcwd():
        app.run(host="0.0.0.0", port=5000)
    else:#if not in docker run in normal localhost
        app.run()
