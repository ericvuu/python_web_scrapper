import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from tkinter import Tk, filedialog

# Function to download resources like images, CSS, and JS while preserving directory structure
def download_resource(url, folder):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            # Extract the directory structure from the URL
            url_parts = url.split('/')
            filename = os.path.join(folder, *url_parts[3:])  # Skip the scheme and domain parts

            # Create the directory structure if it doesn't exist
            directory = os.path.dirname(filename)
            if not os.path.exists(directory):
                os.makedirs(directory)

            # Write the downloaded content to the file
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"Downloaded: {url}")
            return os.path.relpath(filename, folder)  # Return the relative path
        else:
            print(f"Failed to download: {url}")
            return None
    except Exception as e:
        print(f"Error downloading {url}: {str(e)}")
        return None

# Function to scrape the webpage
def scrape(url, project_name, output_folder):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # Create project folder
            project_folder = os.path.join(output_folder, project_name)
            if not os.path.exists(project_folder):
                os.makedirs(project_folder)

            # Download media files (images, GIFs, videos), CSS, and JS while updating references in HTML
            for tag in soup.find_all(['img', 'link', 'script', 'video', 'a']):
                if tag.name == 'img' and tag.has_attr('src'):
                    img_url = urljoin(url, tag['src'])
                    img_filename = download_resource(img_url, project_folder)
                    if img_filename:
                        tag['src'] = img_filename
                elif tag.name == 'link' and tag.has_attr('href') and tag['rel'][0].lower() == 'stylesheet':
                    css_url = urljoin(url, tag['href'])
                    css_filename = download_resource(css_url, project_folder)
                    if css_filename:
                        tag['href'] = css_filename
                elif tag.name == 'script' and tag.has_attr('src'):
                    js_url = urljoin(url, tag['src'])
                    js_filename = download_resource(js_url, project_folder)
                    if js_filename:
                        tag['src'] = js_filename
                elif tag.name == 'video' and tag.has_attr('src'):
                    video_url = urljoin(url, tag['src'])
                    video_filename = download_resource(video_url, project_folder)
                    if video_filename:
                        tag['src'] = video_filename
                elif tag.name == 'a' and tag.has_attr('href'):
                    href_url = urljoin(url, tag['href'])
                    rel_path = os.path.relpath(href_url, url)
                    tag['href'] = rel_path

                    # Check if the href URL is absolute and convert it to relative
                    parsed_href_url = urlparse(href_url)
                    if parsed_href_url.scheme == '' and parsed_href_url.netloc == '':
                        tag['href'] = os.path.relpath(parsed_href_url.path, os.path.dirname(url))

            # Save HTML file
            with open(os.path.join(project_folder, 'index.html'), 'w', encoding='utf-8') as f:
                f.write(str(soup))
            print("HTML file saved successfully.")

            # Extract links from the webpage
            links = [urljoin(url, link['href']) for link in soup.find_all('a', href=True)]
            return links
        else:
            print(f"Failed to fetch URL: {url}")
            return []
    except Exception as e:
        print(f"Error scraping {url}: {str(e)}")
        return []

# Function to crawl the website
def crawl(start_url, project_name, output_folder):
    visited = set()  # Set to keep track of visited URLs
    queue = [start_url]  # Queue to manage URLs to visit

    while queue:
        url = queue.pop(0)  # Get the next URL from the queue
        if url not in visited:
            print(f"Scraping: {url}")
            visited.add(url)
            links = scrape(url, project_name, output_folder)
            for link in links:
                if link not in visited:
                    queue.append(link)  # Add new URLs to the queue

if __name__ == "__main__":
    # Get URL from user input
    start_url = input("Enter the starting URL to scrape: ")

    # Ask user to specify project name
    project_name = input("Enter project name: ")

    # Ask user to select output folder using a file dialog
    root = Tk()
    root.withdraw()  # Hide the main window
    output_folder = filedialog.askdirectory(title="Select Output Folder")
    root.destroy()  # Destroy the main window after selection

    # Crawl the website
    crawl(start_url, project_name, output_folder)
