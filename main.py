# Import necessary libraries
import os
import time
import shutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from instagrapi import Client
import sys
import asyncio
from telegram import Bot, InputMediaPhoto, InputMediaVideo
import pyautogui

# Initialize bot token and channel username
bot_token = '7942062518:AAHpX04fj_hNKXftHiG7_kigx3JeA-DSJLw' 
channel_username = '@testctrpython' 
bot = Bot(token=bot_token) 
 
# Initialize and login to the instagrapi Client 
client = Client() 
client.login('testctrpython', 'alirezahosseini') 
filename_to_url = {}

def initialize_driver():
    # Set Chrome options
    options = Options()
    options.add_argument(r"--user-data-dir=C:\\Users\\Philips\\AppData\\Local\\Google\\Chrome\\User Data\\Default")
    return webdriver.Chrome(options=options)

def download_post(client, media, index, username):
    downloads_folder = 'downloads'
    if not os.path.exists(downloads_folder):
        os.makedirs(downloads_folder)
    user_folder = os.path.join(downloads_folder, username)
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)
    filenames = []
    post_url = f"https://www.instagram.com/p/{media.code}/"
    
    # Download media based on its type
    if media.media_type == 1:  # Photo
        media_path = client.photo_download(media.pk, folder=user_folder)
        new_filename = os.path.join(user_folder, f"{username}_{index+1}{os.path.splitext(media_path)[1]}")
        shutil.move(media_path, new_filename)
        filenames.append(new_filename)
        filename_to_url[new_filename] = post_url
        print(f"Downloaded and renamed {index+1}: {new_filename}")
    elif media.media_type == 2:  # Video
        media_path = client.video_download(media.pk, folder=user_folder)
        new_filename = os.path.join(user_folder, f"{username}_{index+1}{os.path.splitext(media_path)[1]}")
        shutil.move(media_path, new_filename)
        filenames.append(new_filename)
        filename_to_url[new_filename] = post_url
        print(f"Downloaded and renamed {index+1}: {new_filename}")
    elif media.media_type == 8:  # Album
        media_paths = client.album_download(media.pk, folder=user_folder)
        for i, path in enumerate(media_paths):
            new_filename = os.path.join(user_folder, f"{username}_{index+1}_{i+1}{os.path.splitext(path)[1]}")
            shutil.move(path, new_filename)
            filenames.append(new_filename)
            filename_to_url[new_filename] = post_url
            print(f"Downloaded and renamed {index+1}_{i+1}: {new_filename}")
    return filenames

def download_media_posts(post_urls, username, delay=2):
    all_filenames = []
    for index, url in enumerate(post_urls):
        success = False
        while not success:
            try:
                media_pk = client.media_pk_from_url(url)
                media = client.media_info(media_pk)
                filenames = download_post(client, media, index, username)
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

def upload_on_etaa(filenames_and_descriptions, channel_etaa_username):
    driver.get(f"https://web.eitaa.com/#@{channel_etaa_username}")
    time.sleep(10)  # Simplified the two 5-second sleeps

    for filename, description in filenames_and_descriptions:
        print(f"Uploading {filename} with description: {description}")
        
        # Handling upload
        upload_button = driver.find_element(By.XPATH, '//div[@class="btn-icon btn-menu-toggle attach-file tgico-attach"]')
        upload_button.click()
        upload_button1 = driver.find_element(By.XPATH, '//div[@class="btn-menu-item tgico-document rp"]')
        upload_button1.click()
        time.sleep(2)

        file_path = os.path.join(os.getcwd(), filename)  # Construct the full file path
        print(f"File path: {file_path}")
        pyautogui.write(file_path)
        pyautogui.press('enter')

        sys.stdout.reconfigure(encoding='utf-8')
        if description is not None:
            # Handling description
            text_description = driver.find_element(By.XPATH, '//div[@class="input-field-input i18n"]')

            # Remove newlines and filter out non-BMP characters
            bmp_description = filter_bmp_characters(description.replace('\n', ' '))
            print(f"BMP Description: {bmp_description}")
            text_description.send_keys(bmp_description)

        upload_button2 = driver.find_element(By.XPATH, '//button[@class="btn-primary btn-color-primary rp"]')
        upload_button2.click()
        time.sleep(5)

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
            if len(description) > 150:
                description = description[:150]
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
        for post in recent_posts:
            post_url = post.find_element(By.XPATH, ".//a").get_attribute("href")
            top_posts.append((post_url, 9999999999))
    top_posts = sorted(top_posts, key=lambda x: x[1], reverse=True)[:11]
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
    username = "mrbug_ir"
    channel_etaa_username = "testctrpython"
    driver = initialize_driver()

    filenames_and_descriptions = find_posts_get_all_urls(driver, username)
    upload_on_etaa(filenames_and_descriptions, channel_etaa_username)
    driver.implicitly_wait(5)
    driver.quit()
