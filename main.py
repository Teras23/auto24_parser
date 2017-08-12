from bs4 import BeautifulSoup
from urllib.request import urlopen
import json


class Site:
    def __init__(self, url):
        self.url = url

    def parse(self):
        http = urlopen(self.url).read()

    def get_page(self, url=''):
        if url == '':
            url = self.url
        return BeautifulSoup(urlopen(url).read(), 'html.parser')


class Motorcycle(dict):
    def __init__(self, name, price, page_url, picture_url, year=0, motor=0, transmission_type='', mileage=-1):
        dict.__init__(self, name=name, price=price, page_url=page_url, picture_url=picture_url,
                      year=year, motor=motor, transmission_type=transmission_type, mileage=mileage)
        self.name = name
        self.year = year
        self.motor = motor
        self.transmission_type = transmission_type
        self.price = price
        self.page_url = page_url
        self.picture_url = picture_url
        self.mileage = mileage

    def __str__(self):
        return 'Name: {} Year: {} Price: {}'.format(self.name, self.year, self.price)


class MotoSite(Site):
    def __init__(self):
        Site.__init__(self, 'http://www.mototehnika.ee/')
        self.motorcycles = []

    def parse(self):
        front_page = self.get_page()
        motorcycle_category_links = front_page.find_all(class_='item')
        all_motorcycles_links = None

        for item in motorcycle_category_links:
            if len(item.contents) > 1:
                if item.contents[1] == 'Kõik liigid':
                    all_motorcycles_links = item
                    break

        first_all_motorcycles_page = self.get_page(self.url + all_motorcycles_links['href'])
        self.parse_motorcycles(first_all_motorcycles_page)
        motorcycles_json = json.dumps(self.motorcycles)

        with open('motorcycles.json', 'w') as file:
            file.write(motorcycles_json)
            file.close()
        print(self.motorcycles)

    def parse_motorcycles(self, page):
        table = page.find(id='usedVehiclesSearchResult')

        for item in table.contents:
            if item.name == 'tr' and len(item.attrs) > 0:
                picturelink = item.find(class_='pictures').find(class_='small-image').find('img')['src']

                nametable = item.find(class_='make_and_model')
                name = nametable.find('a').string.lstrip()  # lstrip removes starting spaces
                link = nametable.find('a')['href']
                mileage = nametable.find(class_='extra').string

                year = item.find(class_='year').string
                motor = item.find(class_='displacement_cm3').string
                transmission = item.find(class_='transmission').string
                price = item.find(class_='price').string

                motorcycle = Motorcycle(name, price, link, picturelink, year, motor, transmission, mileage)
                self.motorcycles.append(motorcycle)

        next_page_link = None

        page_links = page.find_all(class_='input-link item')

        for link in page_links:
            if link.find(class_='label').string == 'järgmine lk':
                next_page_link = link['href']

        if next_page_link is not None:
            next_page = self.get_page(self.url + next_page_link)
            self.parse_motorcycles(next_page)


def main():
    moto = MotoSite()
    moto.parse()

if __name__ == '__main__':
    main()
