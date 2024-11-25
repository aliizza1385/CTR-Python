
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


# Initialize the bot
bot_token = '7942062518:AAHpX04fj_hNKXftHiG7_kigx3JeA-DSJLw' 
channel_username = '@testctrpython' 
bot = Bot(token=bot_token) 
 
# Initialize and login to the instagrapi Client 
client = Client() 
client.login('testctrpython', 'alirezahosseini') 
filename_to_url ={}

def initialize_driver():
    """
    Initializes and returns a Selenium WebDriver instance.
    """
    options = Options()
    options.add_argument(r"--user-data-dir=C:\\Users\\Philips\\AppData\\Local\\Google\\Chrome\\User Data\\Default")
    return webdriver.Chrome(options=options)

def download_post(client, media, index, username):
    """
    Downloads media (photo, video, album) from a post using instagrapi Client.
    """
    # Create the 'downloads' folder if it doesn't exist
    downloads_folder = 'downloads'
    if not os.path.exists(downloads_folder):
        os.makedirs(downloads_folder)

    # Create the user-specific folder inside the 'downloads' folder
    user_folder = os.path.join(downloads_folder, username)
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)

    filenames = []

    # Construct the post URL using media.code and username
    post_url = f"https://www.instagram.com/p/{media.code}/"

    # Download the media into the user-specific folder
    if media.media_type == 1:  # Photo
        media_path = client.photo_download(media.pk, folder=user_folder)
        new_filename = os.path.join(user_folder, f"{username}_{index+1}{os.path.splitext(media_path)[1]}")
        shutil.move(media_path, new_filename)
        filenames.append(new_filename)
        filename_to_url[new_filename] = post_url  # Store the URL for later use
        print(f"Downloaded and renamed {index+1}: {new_filename}")
    elif media.media_type == 2:  # Video
        media_path = client.video_download(media.pk, folder=user_folder)
        new_filename = os.path.join(user_folder, f"{username}_{index+1}{os.path.splitext(media_path)[1]}")
        shutil.move(media_path, new_filename)
        filenames.append(new_filename)
        filename_to_url[new_filename] = post_url  # Store the URL for later use
        print(f"Downloaded and renamed {index+1}: {new_filename}")
    elif media.media_type == 8:  # Album
        media_paths = client.album_download(media.pk, folder=user_folder)
        for i, path in enumerate(media_paths):
            new_filename = os.path.join(user_folder, f"{username}_{index+1}_{i+1}{os.path.splitext(path)[1]}")
            shutil.move(path, new_filename)
            filenames.append(new_filename)
            filename_to_url[new_filename] = post_url  # Store the URL for later use
            print(f"Downloaded and renamed {index+1}_{i+1}: {new_filename}")

    return filenames


def download_media_posts(post_urls, username, delay=2):
    """
    Downloads media from a list of post URLs and returns a list of filenames.
    Keeps retrying until the download is successful.
    """
    all_filenames = []
    for index, url in enumerate(post_urls):
        success = False
        while not success:
            try:
                # Extract the media PK from the URL and get media info
                media_pk = client.media_pk_from_url(url)
                media = client.media_info(media_pk)
                
                # Download the post and get the filenames
                filenames = download_post(client, media, index, username)
                
                # Extend the list of all filenames
                all_filenames.extend(filenames)
                success = True
            except Exception as e:
                print(f"Failed to download {url}, retrying in {delay} seconds... Error: {e}")
                time.sleep(delay)
    return all_filenames


def extract_url_from_filename(filename):
    """
    Extracts the URL corresponding to a given filename using the filename_to_url dictionary.
    """
    return filename_to_url.get(filename, None)


def find_all_description(driver, filenames):
    """
    Finds all descriptions for a list of filenames and stores them.
    """
    url_description_list = []
    album_description = {}  # Dictionary to store descriptions for album parts

    for filename in filenames:
        # Extract the post URL from the filename
        post_url = extract_url_from_filename(filename)
        if not post_url:
            print(f"URL not found for filename: {filename}")
            url_description_list.append((filename, None))
            continue

        driver.get(post_url)
        driver.implicitly_wait(5)
        
        try:
            # Try finding the description element using different XPaths
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

            # Replace <br> tags with newline characters
            h1_text = h1_html.replace('<br>', '\n')

            # Extract text from <a> tags and replace the <a> tags with their text content
            a_elements = description_element.find_elements(By.TAG_NAME, "a")
            for a in a_elements:
                a_text = a.text
                a_html = a.get_attribute('outerHTML')
                h1_text = h1_text.replace(a_html, a_text)

            description = h1_text
            if len(description) > 50:
                description = description[:50]

            # Check if filename contains a pattern indicating it's part of an album
            if '_' in filename:
                parts = filename.split('_')
                if len(parts) > 2 and parts[-2].isdigit() and parts[-1].split('.')[0].isdigit():
                    album_key = '_'.join(parts[:-1])
                    if album_key not in album_description:
                        album_description[album_key] = description
                    description = album_description[album_key]

            url_description_list.append((filename, description))
            print(f"Description for {filename}: {description}")
        except NoSuchElementException:
            print(f"Description not found for URL: {post_url}")
            url_description_list.append((filename, None))
        except Exception as e:
            print(f"An error occurred while processing URL {post_url}: {str(e)}")

    return url_description_list

async def upload_on_telegram_bot(url_description_list):
    async with bot:
        for filename, description in url_description_list:
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
                print("sending")

def find_posts_get_all_urls(driver, username):
    """
    Finds the top 10 posts of a user by likes using Selenium, and downloads them.
    """
    action = ActionChains(driver)
    driver.get(f"https://www.instagram.com/{username}")
    time.sleep(5)  # Wait for the page to load

    top_posts = []
    # Locate the latest post on the user's profile
    new_post = driver.find_element(By.XPATH, '//div[@class="x1lliihq x1n2onr6 xh8yej3 x4gyw5p x1ntc13c x9i3mqj x11i5rnm x2pgyrj"]')
    new_post_url = new_post.find_element(By.XPATH, ".//a").get_attribute("href")
    action.move_to_element(new_post).perform()

    try:
        like_text = post.find_element(By.XPATH, ".//span[@class='x1lliihq x1plvlek xryxfnj x1n2onr6 x1ji0vk5 x18bv5gf x193iq5w xeuugli x1fj9vlw x13faqbe x1vvkbs x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x1i0vuye xl565be x1xlr1w8 x9bdzbf x10wh9bi x1wdrske x8viiok x18hxmgj']").text
        post_set = set()
        last_height = driver.execute_script("return document.body.scrollHeight")

        while True:
            # Find new posts
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
            time.sleep(2)  # Add delay to avoid rate limiting

            # Check if the end of the page is reached
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    except Exception as e:
        recent_posts = driver.find_elements(By.XPATH, '//div[@class="x1lliihq x1n2onr6 xh8yej3 x4gyw5p x1ntc13c x9i3mqj x11i5rnm x2pgyrj"]')
        for post in recent_posts:
            post_url = post.find_element(By.XPATH, ".//a").get_attribute("href")
            top_posts.append((post_url, 9999999999))

    # Sort posts by likes and get the top 10
    top_posts = sorted(top_posts, key=lambda x: x[1], reverse=True)[:11]
    top_posts_urls = [post_url for post_url, like in top_posts]

    print("Top 11 posts with most likes:")
    for post_url, like in top_posts:
        print(f"Post URL: {post_url}, Likes: {like}")

    # Download media from the top posts and get filenames
    filenames = download_media_posts(top_posts_urls, username)

    # Get descriptions for the top posts
    url_description_list = find_all_description(driver, filenames)

    # Upload files to Telegram
    asyncio.run(upload_on_telegram_bot(url_description_list))


if __name__ == "__main__":
    # Set the output encoding to utf-8
    sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
    
    username = "magoolime"
    driver = initialize_driver()
    find_posts_get_all_urls(driver, username)
    driver.implicitly_wait(5)
    driver.quit()  # Ensure the driver is properly closed