from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
import numpy as np
import pickle
import time
import urllib.request
import time
import os
import cv2


DRIVER_PATH = r"Code\DatasetCreation\driver\chromedriver.exe"
IMAGES_PATH = r"Code\DatasetCreation\images"
genre_to_label = {'drama': 0, 'comedy': 1, 'action': 2, 'thriller': 3,
                  'romance': 4, 'animation': 5}

s = Service(DRIVER_PATH)
driver = webdriver.Chrome(service=s)
driver.get('https://www.google.com/imghp?hl=en')

flag = 1


def fetch_banner(movie_name, images_path=IMAGES_PATH):
    global flag
    # for a single movie following method was fine but since we have multiple movies in our dataset so this is inefficient since we need to close driver and open it again for each movie
    # search_url = f"https://www.google.com/search?safe=off&site=&tbm=isch&source=hp&q={movie_name}+movie&oq={movie_name}+movie&gs_l=img"
    # driver.get(search_url)
    # code for image fetching
    # driver.close()
    # taking around 10-13 seconds for one image to fetch

    if flag == 1:  # for first time element path is a bit different
        search_box = driver.find_element(
            By.CSS_SELECTOR, "input.gLFyf.gsfi")  # input box selector
        flag += 1
    else:
        search_box = driver.find_element(
            By.CSS_SELECTOR, "input#REsRA")  # input box selector
    search_box.send_keys(f"{movie_name} movie")  # search for the movie
    search_box.send_keys(Keys.ENTER)  # hit enter

    thumbnail_results = driver.find_elements(By.CSS_SELECTOR, "img.Q4LuWd")
    first_thumbnail = thumbnail_results[0]
    src = first_thumbnail.get_attribute("src")
    urllib.request.urlretrieve(src, f"{images_path}\{movie_name}.png")

    # clear the search box
    search_box = driver.find_element(By.CSS_SELECTOR, "input#REsRA")
    search_box.send_keys(Keys.CONTROL + 'a', Keys.BACKSPACE)


def get_images(df):
    for _, row in df.iterrows():
        print("Fetching image for:", row["Title"])
        movie_name = row["Title"]
        fetch_banner(movie_name)
        print("Image fetched for:", row["Title"])

        print("-"*50)


def to_pickle(output, filename, IMAGES_PATH=IMAGES_PATH):
    for i, file_name in enumerate(os.listdir(IMAGES_PATH)):
        movie_title = file_name.split(".")[0]
        row_list = list()
        row_list.append(movie_title)

        row = df[df["Title"] == movie_title]
        genre = row["Genre"].values[0]
        # genre_id = genre_to_label[genre]
        row_list.append(genre)

        banner = cv2.imread(f"{IMAGES_PATH}\{file_name}")
        banner = cv2.cvtColor(banner, cv2.COLOR_BGR2RGB)
        resized_banner = cv2.resize(banner, (224, 224))
        row_list.append(resized_banner)

        output.append(row_list)

    with open(f"Code\DatasetCreation\{filename}.pickle", "wb") as f:
        pickle.dump(output, f)


df = pd.read_csv(r"Dataset\Text\MovieTopGenres (1).csv")
start_index = 0
end_index = 5

output = list()

get_images(df[start_index:end_index])
to_pickle(output, filename=f"{start_index}_{end_index}")

driver.close()
