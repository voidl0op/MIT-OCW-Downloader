from urllib.request import urlretrieve
from urllib.parse import urljoin, urlparse
from pathlib import Path
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://ocw.mit.edu"

def get_soup(url):
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")

def make_absolute(base_url, href):
    if not href:
        return None
    return urljoin(base_url, href)

def get_download_page(course_url):
    soup = get_soup(course_url)
    link = soup.find("a", class_="download-course-link-button")
    if not link:
        print("Download page link not found.")
        return None
    href = link.get("href")
    return make_absolute(course_url, href)

def get_resource_pages(download_url):
    soup = get_soup(download_url)
    resources = []
    for link in soup.find_all("a", class_="resource-list-title"):
        href = link.get("href")
        if href:
            resources.append(make_absolute(download_url, href))
    return resources

def get_file_url(resource_url):
    soup = get_soup(resource_url)
    link = soup.find("a", class_="download-file")
    if not link:
        return None
    href = link.get("href")
    return make_absolute(resource_url, href)

def get_filename(file_url):
    path = urlparse(file_url).path
    filename = Path(path).name
    if not filename:
        filename = "downloaded_file"
    return filename

def download_file(file_url, download_folder):
    filename = get_filename(file_url)
    target_path = download_folder / filename
    print(f"Downloading: {filename}")
    urlretrieve(file_url, target_path)
    print(f"Saved: {target_path}")

def download_course_resources(course_url, folder):
    download_folder = Path(folder)
    download_folder.mkdir(parents=True, exist_ok=True)

    print("Searching for course download page...")
    download_page = get_download_page(course_url)
    if not download_page:
        return

    print(f"Download page found:\n{download_page}\n")
    print("Searching for resource pages...")
    resource_pages = get_resource_pages(download_page)
    print(f"Found {len(resource_pages)} resource page(s).\n")

    for index, resource_url in enumerate(resource_pages, start=1):
        print(f"[{index}/{len(resource_pages)}] Processing:")
        print(resource_url)
        try:
            file_url = get_file_url(resource_url)
            if file_url:
                print(f"File found: {file_url}")
                download_file(file_url, download_folder)
            else:
                print("No downloadable file found.")
        except Exception as e:
            print(f"Error: {e}")
        print("-" * 60)

    print("Finished.")