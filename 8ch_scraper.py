#! /usr/bin/env python3

# 8ch_scraper downloads all "png", "jpg", and "gif" images from a thread

import os
import sys
import random
import requests
import bs4
from urllib.parse import urljoin
import logging
logging.basicConfig(level=logging.DEBUG, format=" %(asctime)s - %(levelname)s - %(message)s")
logging.disable(logging.DEBUG)


def parse_urls_and_filenames(elem, pic_urls, filenames, is_op=False):
    # Parse element for media urls and filenames.
    # Results are appended to the respective lists.

    for e in elem:
        # div format:
        #  <div_elem>.files.(space,file,space,file,space,...).file_info.(text,a<href>,space,span<class=unimportant>)
        # it's possible there are multiple media files per post, so we need to iterate each file in files, skipping 1 for the empty element.
        if is_op:
            num_files = len(e.contents)
        else:
            num_files = len(e.contents[2].contents)

        for i in range(1, num_files, 2):
            try:

                if is_op:
                    pic_elem = e.contents[i].contents[0].contents[1]
                    fn_elem = e.contents[i].contents[0].contents[3].contents[1]                    
                else:
                    pic_elem = e.contents[2].contents[i].contents[0].contents[1]
                    fn_elem = e.contents[2].contents[i].contents[0].contents[3].contents[1]
                # get the url for the media file
                pic_urls.append(pic_elem["href"])
                # get the name for the media file
                try:
                    # (title attribute represents the original filename)
                    filenames.append(fn_elem["title"])
                except KeyError:
                    # if there's no title attribute, default to the filename element text (this is NOT the original filename)
                    logging.debug("(KeyError) couldn't find the title attribute for a filename element, defaulting to filename element text...")
                    try:
                        filenames.append(fn_elem.text)
                    except:
                        logging.debug("while defaulting to filename element text, no text was found!  empty string has been appended to maintain url / filename sync...")
                        filenames.append("")
                        pass
            except IndexError:
                logging.debug("(IndexError) found post with file but post element is structured differently, so skipping...")
                pass
            except KeyError:
                logging.debug("(KeyError) found media element but couldn't find url, so skipping...")
                pass
    

def get_image_urls(url, retry=0):
    # Return a list of all image links found at url.
    # If the get request fails it will be retried up to (retry) times
    # before returning an empty list.
    if retry > 50:
        retry = 50
    resp = requests.get(url)
    try:
        resp.raise_for_status()
    except:
        if retry > 0:
            return get_image_urls(url, retry - 1)
        else:
            return []
    soup = bs4.BeautifulSoup(resp.text, "lxml")

    pic_urls = []
    filenames = []
    # get OP media files
    op_files_elem = soup.find_all("div", class_="files", limit=1)
    parse_urls_and_filenames(op_files_elem, pic_urls, filenames, is_op=True)
    
    # get media files posted in replies
    div_elems = soup.find_all("div", class_="has-file")
    parse_urls_and_filenames(div_elems, pic_urls, filenames)
                
    return (pic_urls, filenames)


def save_media(urls, filenames, force_dl = False):
    # Save media from urls, to filenames.
    # Filenames are assumed absolute.
    # If force_dl is False then if a filename already exists in the directory it will not be redownloaded.
    # If force_dl is True then all media files will be downloaded and any existing file in the directory with
    # the same name as a downloaded file will be overwritten.
    # Any downloads that fail will be returned in the failed_downloads dictionary [key=filename, value=url]
    failed_downloads = {}
    if force_dl:
        for i in range(len(filenames)):
            save_file(urls[i], filenames[i])
    else:
        for i in range(len(filenames)):
            if not os.path.isfile(filenames[i]):
                try:
                    save_file(urls[i], filenames[i])
                except requests.exceptions.ConnectionError:
                    failed_downloads[filenames[i]] = urls[i]
            else:
                logging.info("file already exists in download directory, so skipping...\n\tfile:\t" + filenames[i] + "\n")
    return failed_downloads
    

def save_file(url, filename):
    # Save the file at url, to filename.
    print("\ndownloading file from:\n" + url)
    resp = requests.get(url, stream=True)
    total_length = resp.headers.get("content-length")
    try:
        resp.raise_for_status()
    except:
        logging.debug("error downloading file:\t" + url)
        print("error downloading file:\t" + url)
        return

    chunk_size = 4096
    with open(filename, "wb") as out_file:
        print("saving to filename:\t" + filename)
        if total_length is None:
            out_file.write(resp.content)
        else:
            print()
            dl = 0
            total_length = int(total_length)
            for data in resp.iter_content(chunk_size):
                dl += len(data)
                out_file.write(data)
                print("\r" + str(int(100 * (dl / total_length))) + "%", end="")
    print("\ndownload complete!")


def make_abs_filenames(filenames, dl_dir):
    # Make filenames absolute by joining the download_directory and the filenames.
    for i in range(len(filenames)):
        filenames[i] = os.path.join(dl_dir, filenames[i])


def make_unique_filenames(filenames):
    # Check there are no duplicate filenames.
    # If there are duplicates, append a random number to rename the duplicate.    
    uniq = set()
    dup = []
    for f in filenames:
        if f in uniq:
            dup.append(f)
        else:
            uniq.add(f)
    for i in range(len(filenames)):
        if filenames[i] in dup:
            dup.remove(filenames[i])
            logging.debug("duplicate filename:\t" + filenames[i])
            filenames[i] = filenames[i] + "_" + str(random.randint(1,999999999))
            logging.debug("renamed to:\t" + filenames[i])
    if not dup == []:
        make_unique_filenames(filenames)
        

    
USAGE_MESSAGE = "usage: ./8ch_scraper thread_url dl_dir=./8ch_media_(op_postnum), force_download=False"

if len(sys.argv) != 2 and len(sys.argv) != 3 and len(sys.argv) != 4:
    print(USAGE_MESSAGE)
    sys.exit(0)

url = sys.argv[1]

url_keys = url.split("/")
media_thread_id = url_keys[len(url_keys) - 3] + "_" + url_keys[len(url_keys) - 1].split(".")[0]
dl_dir = "./8ch_media_" + media_thread_id
if len(sys.argv) > 2:
    dl_dir = sys.argv[2]

force_dl = False
if len(sys.argv) == 4:
    if sys.argv[3] == "True":
        force_dl = True
    

# Scrape the media urls and media filenames from the url.
try:
    image_urls, filenames = get_image_urls(url, 10) # currently the op images aren't grabbed because they're in a different section
except requests.exceptions.ConnectionError:
    print("Connection error... try again later?")
    sys.exit(0)
    
#sys.exit(0)
# Make the filenames absolute and rename duplicates.
make_abs_filenames(filenames, dl_dir)
make_unique_filenames(filenames)
# Create the download directory if it doesn't exist.
if not os.path.isdir(dl_dir):
    os.mkdir(dl_dir)

# Save the media files to the download directory using absolute media filenames.
while(True):
    failed_dls = save_media(image_urls, filenames, force_dl)
    if len(failed_dls) == 0:
        break
    print("Failed downloads:")
    for v in failed_dls.values():
        print("\t" + v)
        
    val = str.lower(input("retry? (y / n): "))
    if(val == "y"):
        filenames = list(failed_dls.keys())
        image_urls = list(failed_dls.values())
    else:
        break


