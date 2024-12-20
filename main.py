# Import necessary libraries
import os
import time
import shutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import sys
import asyncio
from telegram import Bot, InputMediaPhoto, InputMediaVideo
import instaloader
import fnmatch
from environs import Env

# Load environment variables from .env file
env = Env()
env.read_env()

L = instaloader.Instaloader()
# Initialize bot token and channel username
bot_token = env('BOT_TOKEN_TELEGRAM') 
channel_username = env('CHANNEL_TELEGRAM_USERNAME')
bot = Bot(token=bot_token)

client = instaloader.Instaloader()
filename_to_url = {}

user_data_dirs = os.getenv('USER_DATA_DIRS')


def initialize_driver(user_data_dir):
    options = webdriver.ChromeOptions()
    options.add_argument(f'--user-data-dir={user_data_dir}')
    options.add_argument('--headless')
    caps = DesiredCapabilities.CHROME.copy()

    for key, value in caps.items():
        options.set_capability(key, value)

    driver = webdriver.Remote(
        command_executor='http://localhost:4444/wd/hub',
        options=options
    )
    
    return driver

def delete_unnecessary_files(user_folder, username):
    pattern = f"{username}_*.*"
    for item in os.listdir(user_folder):
        if not fnmatch.fnmatch(item, pattern):
            os.remove(os.path.join(user_folder, item))
            print(f"Removed {item}")

def download_post(client, post, index, username):

    filenames = []
    post_url = f"https://www.instagram.com/p/{post.shortcode}/"
    
    # Ensure the user folder exists
    downloads_folder = 'downloads'
    if not os.path.exists(downloads_folder):
        os.makedirs(downloads_folder)
    # Download media based on its type
    if post.typename == 'GraphVideo':  # Video
        media_path = os.path.join(downloads_folder, f"{username}_{index+1}.mp4")
        client.download_post(post, target=downloads_folder)
        # Rename downloaded files
        for item in os.listdir(downloads_folder):
            if item.endswith('.mp4') and not item.startswith(username):
                if not os.path.exists(media_path):
                    os.rename(os.path.join(downloads_folder, item), media_path)
                else:
                    os.remove(os.path.join(downloads_folder, item))  # Remove duplicate file
                print(f"Downloaded and renamed {index+1}: {media_path}")
                filenames.append(media_path)
                filename_to_url[media_path] = post_url
                break
        
    elif post.typename == 'GraphImage':  # Single Image
        media_path = os.path.join(downloads_folder, f"{username}_{index+1}.jpg")
        client.download_post(post, target=downloads_folder)
        # Rename downloaded files
        for item in os.listdir(downloads_folder):
            if item.endswith('.jpg') and not item.startswith(username):
                if not os.path.exists(media_path):
                    os.rename(os.path.join(downloads_folder, item), media_path)
                else:
                    os.remove(os.path.join(downloads_folder, item))  # Remove duplicate file
                print(f"Downloaded and renamed {index+1}: {media_path}")
                filenames.append(media_path)
                filename_to_url[media_path] = post_url
                break
    
    elif post.typename == 'GraphSidecar':  # Album
        client.download_post(post, target=downloads_folder)
        for i, sidecar_node in enumerate(post.get_sidecar_nodes()):
            extension = 'mp4' if sidecar_node.is_video else 'jpg'
            media_path = os.path.join(downloads_folder, f"{username}_{index+1}_{i+1}.{extension}")
            # Rename downloaded files
            for item in os.listdir(downloads_folder):
                if item.endswith(f".{extension}") and not item.startswith(username):
                    if not os.path.exists(media_path):
                        os.rename(os.path.join(downloads_folder, item), media_path)
                    else:
                        os.remove(os.path.join(downloads_folder, item))  # Remove duplicate file
                    print(f"Downloaded album item {i+1}: {media_path}")
                    filenames.append(media_path)
                    filename_to_url[media_path] = post_url
                    break
    
    delete_unnecessary_files(downloads_folder, username)

    return filenames

def download_media_posts(post_urls, username, delay=2):
    all_filenames = []
    for index, url in enumerate(post_urls):
        success = False
        while not success:
            try:
                post = instaloader.Post.from_shortcode(client.context, url.split("/")[-2])
                filenames = download_post(client, post, index, username)
                all_filenames.extend(filenames)
                success = True
            except Exception as e:
                print(f"Failed to download {url}, retrying in {delay} seconds... Error: {e}")
                time.sleep(delay)
    return all_filenames



def extract_url_from_filename(filename):
    return filename_to_url.get(filename, None)

def filter_bmp_characters(text):
    return ''.join(char for char in text if ord(char) <= 0xFFFF)

def upload_on_etaa(filenames_and_descriptions, channel_etaa_username, driver, compression):
    driver.get(f"https://web.eitaa.com/#{channel_etaa_username}")
    time.sleep(10)  # Simplified the two 5-second sleeps

    for filename, description in filenames_and_descriptions:
        # Construct the full file path
        file_path = os.path.join(os.getcwd(), filename)
 
        file_input = driver.find_element(By.XPATH, '//input[@type="file"]')
        file_input.send_keys(file_path)
        time.sleep(2)

        sys.stdout.reconfigure(encoding='utf-8')
        time.sleep(2)
        
        if description is not None:
            # Handling description
            text_description = driver.find_element(By.XPATH, '//div[@class="input-field-input i18n"]')
            # Remove newlines and filter out non-BMP characters
            bmp_description = filter_bmp_characters(description.replace('\n', ' '))
            text_description.send_keys(bmp_description)
        
        # Find the compression checkbox
        check_input_compression = driver.find_element(By.XPATH, '//input[@id="input-compress-items"and@class="checkbox-field-input"]')
        button_click_compression = driver.find_element(By.XPATH, '//span[@class="checkbox-caption i18n"]')

        if compression is True:
            if check_input_compression.is_selected():
                button_click_compression.click()
            else:
                pass
        else:
            if check_input_compression.is_selected():
                pass
            else:
                button_click_compression.click()

        upload_button2 = driver.find_element(By.XPATH, '//button[@class="btn-primary btn-color-primary rp"]')
        upload_button2.click()
        time.sleep(5)
    time.sleep(10)

def find_all_description(driver, filenames):
    filenames_and_descriptions = []
    album_description = {}
    for filename in filenames:
        post_url = extract_url_from_filename(filename)
        if not post_url:
            print(f"URL not found for filename: {filename}")
            filenames_and_descriptions.append((filename, None))
            continue
        driver.get(post_url)
        driver.implicitly_wait(5)
        try:
            description_element = None
            possible_xpaths = [
                '//h1[@class="_ap3a _aaco _aacu _aacx _aad7 _aade"]',
                '//span[@class="x193iq5w xeuugli x1fj9vlw x13faqbe x1vvkbs xt0psk2 x1i0vuye xvs91rp xo1l8bm x5n08af x10wh9bi x1wdrske x8viiok x18hxmgj"]'
            ]
            for xpath in possible_xpaths:
                try:
                    description_element = driver.find_element(By.XPATH, xpath)
                    break
                except NoSuchElementException:
                    continue
            if not description_element:
                raise NoSuchElementException("No valid description element found")
            h1_html = description_element.get_attribute('innerHTML')
            h1_text = h1_html.replace('<br>', '\n')
            a_elements = description_element.find_elements(By.TAG_NAME, "a")
            for a in a_elements:
                a_text = a.text
                a_html = a.get_attribute('outerHTML')
                h1_text = h1_text.replace(a_html, a_text)
            description = h1_text
            if len(description) > 250:
                description = description[:250]
            if '_' in filename:
                parts = filename.split('_')
                if len(parts) > 2 and parts[-2].isdigit() and parts[-1].split('.')[0].isdigit():
                    album_key = '_'.join(parts[:-1])
                    if album_key not in album_description:
                        album_description[album_key] = description
                    description = album_description[album_key]
            filenames_and_descriptions.append((filename, description))
            print(f"Description for {filename}: {description}")
        except NoSuchElementException:
            print(f"Description not found for URL: {post_url}")
            filenames_and_descriptions.append((filename, None))
        except Exception as e:
            print(f"An error occurred while processing URL {post_url}: {str(e)}")
    return filenames_and_descriptions

async def upload_on_telegram_bot(filenames_and_descriptions):
    async with bot:
        for filename, description in filenames_and_descriptions:
            try:
                media = None
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                    media = InputMediaPhoto(open(filename, 'rb'), caption=description)
                elif filename.lower().endswith('.mp4'):
                    media = InputMediaVideo(open(filename, 'rb'), caption=description)
                if media:
                    await bot.send_media_group(chat_id=channel_username, media=[media])
                    print(f"Uploaded: {filename}")
            except FileNotFoundError:
                print(f"File not found: {filename}")
            except Exception as e:
                print("uploading")

def find_posts_get_all_urls(driver, username):
    action = ActionChains(driver)
    driver.get(f"https://www.instagram.com/{username}")
    time.sleep(5)
    top_posts = []
    new_post = driver.find_element(By.XPATH, '//div[@class="x1lliihq x1n2onr6 xh8yej3 x4gyw5p x1ntc13c x9i3mqj x11i5rnm x2pgyrj"]')
    new_post_url = new_post.find_element(By.XPATH, ".//a").get_attribute("href")
    action.move_to_element(new_post).perform()
    try:
        post_set = set()
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            new_posts = driver.find_elements(By.XPATH, '//div[@class="x1lliihq x1n2onr6 xh8yej3 x4gyw5p x1ntc13c x9i3mqj x11i5rnm x2pgyrj"]')
            for post in new_posts:
                post_url = post.find_element(By.XPATH, ".//a").get_attribute("href")
                if new_post_url not in post_set:
                    post_set.add(new_post_url)
                    top_posts.append((new_post_url, 9999999999))
                if post_url not in post_set:
                    post_set.add(post_url)
                    action.move_to_element(post).perform()
                    like_text = post.find_element(By.XPATH, ".//span[@class='x1lliihq x1plvlek xryxfnj x1n2onr6 x1ji0vk5 x18bv5gf x193iq5w xeuugli x1fj9vlw x13faqbe x1vvkbs x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x1i0vuye xl565be x1xlr1w8 x9bdzbf x10wh9bi x1wdrske x8viiok x18hxmgj']").text
                    if 'K' in like_text:
                        like = int(float(like_text.replace('K', '')) * 1000)
                    elif 'M' in like_text:
                        like = int(float(like_text.replace('M', '')) * 1000000)
                    else:
                        like = int(like_text.replace(',', ''))
                    top_posts.append((post_url, like))
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
    except Exception as e:
        recent_posts = driver.find_elements(By.XPATH, '//div[@class="x1lliihq x1n2onr6 xh8yej3 x4gyw5p x1ntc13c x9i3mqj x11i5rnm x2pgyrj"]')
        top_posts.clear()
        for post in recent_posts:
            post_url = post.find_element(By.XPATH, ".//a").get_attribute("href")
            top_posts.append((post_url, 9999999999))

    top_posts = sorted(top_posts, key=lambda x: x[1], reverse=True)[:10]
    top_posts_urls = [post_url for post_url, like in top_posts]
    print("Top 11 posts with most likes:")
    for post_url, like in top_posts:
        print(f"Post URL: {post_url}, Likes: {like}")
    filenames = download_media_posts(top_posts_urls, username)
    filenames_and_descriptions = find_all_description(driver, filenames)
    asyncio.run(upload_on_telegram_bot(filenames_and_descriptions))
    return filenames_and_descriptions

if __name__ == "__main__":
    sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
    
    # Fetch environment variables
    username = os.getenv('USERNAME_INSTAGRAM_FOR_DOWNLOADS_POSTS')
    channel_etaa_username = os.getenv('EITAA_CHANNEL_USERNAME')
    compression = os.getenv('COMPRESSION', 'false').lower() in ('true', '1', 't')
    
    driver = initialize_driver(user_data_dirs)
    
    filenames_and_descriptions = find_posts_get_all_urls(driver, username)
    upload_on_etaa(filenames_and_descriptions, channel_etaa_username, driver, compression)
    
    driver.implicitly_wait(5)
    driver.quit()

