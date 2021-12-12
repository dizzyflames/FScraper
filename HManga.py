import re
import requests
import xml.etree.cElementTree as ET
from bs4 import BeautifulSoup
from difflib import SequenceMatcher

file_name = "[Shake] Yukina Tachibana's Compensated Dating Journal 3.zip"


# https://www.fakku.net/hentai/yukina-tachibanas-compensated-dating-journal-3-english

# This class will scrape the relevant manga on Fakku and create an XML file
# that can be used to provide metadata for comic programs like ComicRack
class HManga:
    base_web = ''
    weblist = []
    title = ''
    artist = ''
    parody = ''
    magazine = ''
    publisher = ''
    summary = ''
    tags = ''
    adult = True
    fakku = "https://www.fakku.net/hentai/"
    source = ''
    file_name = ''
    circle = ''
    book = ''
    event = ''
    xml = ''

    # Populates all class variables, if we have website, we can directly get data.
    # If not, create website link from filename following a specific format.
    def __init__(self, filename='', website=''):
        '''
        Check if file name is valid
        if it is valid, generate website link
        if it is not valid, do nothing

        :param filename:
        :param website:
        '''
        self.base_web = ''
        self.weblist = []
        self.title = ''
        self.artist = ''
        self.parody = ''
        self.magazine = ''
        self.publisher = ''
        self.magazine = ''
        self.publisher = ''
        self.summary = ''
        self.tags = ''
        self.adult = True
        self.source = ''
        self.circle = ''
        self.book = ''
        self.event = ''
        self.xml = ''

        if self.validate_filename(filename):
            self.generate_website(filename)

        if website is not None:
            try:
                self.fakku_scrape()
            except requests.exceptions.MissingSchema:
                with open('errors.txt', 'w') as f:
                    f.write('errors: ' + Exception + " (" + filename + ")\n")

        self.create_xml()

    def validate_filename(self, file):
        '''
        Validates provided url to match the format.
        Will assign the file name, artist, and title based on the filename provided
        Uses regex to determine if there is a match.

        Returns True or False
        '''
        self.file_name = file
        self.artist = re.search(r'\[.+\]', file).group()[1:-1]
        self.title = re.sub(r"(\[.*\]|\(.*\))", "", file).strip()
        self.title = re.sub(r"\.zip", "", self.title).strip()
        return re.match(r"\[[^\][()]+\][^(]+(?:\([^\][()]+\))?\.zip", file)

    def similarity(self, new_web):
        '''
        Sequence matcher to determine how close the new website is to the currently assigned one.
        returns a number from 0 to 1, 1 being identical.

        :return:
        '''
        return SequenceMatcher(None, self.base_web, new_web)

    def generate_website(self, filename):
        '''
        Generates a website url based on the provided file name
        Will also assign the website url and html source
        Returns the error code of the website.
        Should return 200 if website is working properly.

        :param self:
        :param filename:
        :return:
        '''

        # remove contents square brackets and text inside
        site = re.sub(r'\[[^)]*\]', '', filename).strip()
        site = site.replace('.zip', '')

        # remove ending round brackets
        if "Full Color Version" not in site:
            site = re.sub(r'[ ]\([^)]*\)', '', site)
        else:
            site.replace('(Full Color Version)', 'Full Color Version')
        site = site.replace(' ', '-')
        site = re.sub(r"[^a-zA-Z0-9-’]", '', site)
        site = self.fakku + site.lower()
        site += '-english'
        self.base_web = site
        soup = BeautifulSoup(requests.get(site).content, 'html.parser')
        self.source = soup
        return self.source.ok

    def fakku_scrape(self):
        '''
        Scrapes the fakku.net for hentai metadata
        Will check if the class website is valid, if not, it will scrape the website from the artist based on closes
        matching website link.

        :return:
        '''

        # page = requests.get(self.web)

        works = self.fakku_scrape_artist()
        chapter = re.search(r'[0-9][0-9]?-english', self.base_web)
        ch = ''
        if chapter:
            ch = chapter.group(0)

        for work in works:
            ratio = self.similarity('https://www.fakky.net/' + work['href']).ratio()
            if 0.9 < ratio:
                new_web = "https://www.fakku.net" + work['href']

                if ch is None or ch in new_web:
                    self.weblist.append(new_web)

        page = ''
        try:
            page = requests.get(self.weblist[0])
        except IndexError:
            print(self.file_name + " does not exist.")
            f = open('errors.txt', 'w', encoding='utf-8')
            f.write(self.file_name)
            f.close()
            return

        soup = BeautifulSoup(page.content, 'html.parser')
        self.source = soup

        self.title = soup.find('a', {'href': re.compile(r'\/hentai\/(\S+)')}).get_text()

        self.artist = soup.find('a', {'href': re.compile(r'\/artists\/(\S+)')}).get_text().replace('\r\n\t\t', '')

        self.parody = soup.find('a', {'href': re.compile(r'\/series\/(\S+)')}).get_text().replace('\r\n\t\t', '')

        circle = soup.find('a', {'href': re.compile(r'\/circles\/(\S+)')})
        if circle is not None:
            self.circle = circle.get_text().replace('\r\n\t\t', '')
        else:
            self.circle = ''

        magazine = soup.find('a', {'href': re.compile(r'\/magazines\/(\S+)')})
        if magazine is not None:
            self.magazine = magazine.get_text().replace('\r\n\t\t', '')
        else:
            self.magazine = ''

        event = soup.find('a', {'href': re.compile(r'\/events\/(\S+)')})
        if event is not None:
            self.event = event.get_text().replace('\r\n\t\t', '')
        else:
            self.event = ''

        self.publisher = soup.find('a', {'href': re.compile(r'\/publishers\/(\S+)')}).get_text().replace('\r\n\t\t', '')

        books = soup.findAll('div',
                             {'class': 'inline-block w-24 text-left align-top'})  # .nextSibling.nextSibling.get_text()
        for book in books:
            if book.get_text() == 'Book':
                self.book = book.next_sibling.next_sibling.get_text()

        self.summary = soup.find('meta', {'name': 'description'}).get_attribute_list("content")[0].strip()

        tags = soup.findAll('a', {'href': re.compile(r'\/tags\/(\S+)')})
        for i in range(len(tags)):
            tags[i] = tags[i].get_text().replace('\r\n\t\t', '')
        self.tags = tags

        if 'Non-H' in tags:
            self.adult = False

    def fakku_scrape_artist(self):
        '''
        Scrapes the manga artist from fakku.net and returns a list of all of the artist's work from the website.

        :return:
        '''
        art = self.artist.replace(" ", "-").lower()
        fakku_art = "https://www.fakku.net/artists/" + art
        page = requests.get(fakku_art)

        if page.ok:
            soup = BeautifulSoup(page.content, 'html.parser')
            works = soup.findAll('a', {'href': re.compile(r'/hentai/'), 'title': re.compile(r'.+')})
            return works

    def get_website(self):
        return self.web

    def get_title(self):
        return self.title

    def get_artist(self):
        return self.artist

    def get_parody(self):
        return self.parody

    def get_magazine(self):
        return self.magazine

    def get_publisher(self):
        return self.adult

    def get_summary(self):
        return self.summary

    def get_tags(self):
        return self.tags

    def isAdult(self):
        return self.adult

    def get_xml(self):
        return self.xml

    # function accepts the file name and creates a comicinfo xml file of that file
    def create_xml(self):
        root = ET.Element("ComicInfo")
        root.attrib['xmlns:xsd'] = "http://www.w3.org/2001/XMLSchema"
        root.attrib['xmlns:xsi'] = "http://www.w3.org/2001/XMLSchema-instance"
        ET.SubElement(root, "Title").text = self.title
        ET.SubElement(root, 'AlternateSeries').text = self.parody
        ET.SubElement(root, 'Summary').text = self.summary
        ET.SubElement(root, 'Year').text = '2017'  # Hardcoded for now
        ET.SubElement(root, 'Month').text = '03'  # Hardcoded for now
        ET.SubElement(root, 'Writer').text = self.artist
        ET.SubElement(root, 'Publisher').text = self.publisher
        ET.SubElement(root, 'Genre').text = ", ".join(self.tags)
        ET.SubElement(root, 'Web').text = self.weblist[0] if len(self.weblist) > 0 else ''
        ET.SubElement(root, 'LanguageISO').text = 'en'
        ET.SubElement(root, 'Manga').text = 'Yes'
        ET.SubElement(root, 'SeriesGroup').text = self.magazine
        if not self.adult:
            ET.SubElement(root, 'AgeRating').text = 'Not Adults Only'
        else:
            ET.SubElement(root, 'AgeRating').text = 'Adults Only 18+'

        tree = ET.ElementTree(root)
        tree.write("SampleXML.xml")
        self.xml = tree

    # accepts an array of filenames and creates an xml file of all included filenames
    def xml_multiple(self, mangas):
        pass

    # recursively create xml of all files in folder or in nested folders
    def xml_recursive(self, folder):
        pass

    '''
    find similarity metric:
    
    from difflib import SequenceMatcher

    def similar(a, b):
        return SequenceMatcher(None, a, b).ratio()
        
    correct one if 90% similarity metric
    '''

    '''
    if no url match, pull artist name and find closest url
    '''
