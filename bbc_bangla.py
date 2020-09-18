'''
MIT License

Copyright (c) 2020 MD ATAUR RAHMAN

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

#This code is written in Botton-Up fashion
# import libraries
import os
import urllib.request
from bs4 import BeautifulSoup
from weasyprint import HTML


# this function gets the news (text) from a single page
def get_data(page):

    title = []
    contents = []

    # parse the html using beautiful soup and store in variable `soup`
    soup = BeautifulSoup(page, 'html.parser')

    try:
        # Getting the <title>
        title = soup.find('title')
        title = title.text.strip() # strip() is used to remove starting and trailing spaces
        # print(title)

        # Getting the main texts inside <p>
        contents = soup.find('div', attrs={'class': 'StyledDiv-sc-1dngwtn-0 riLLS'})
        texts =  contents.find_all('p')
        contents = []
        for line in texts:
            contents.append(line.getText().split('\n')[0])      #removing the HMTL tags
        # print(texts)

    except:
        print("Page Doesn't Contain any News Article.")

    return title, contents


# Writing the output into .txt files
def write_text_file(file_name, title, contents):

    # if directory/folder given doesn't exists
    out_dir = "output/"
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    file_name = out_dir + file_name + '.txt'

    with open(file_name, 'w', encoding='utf-8') as out_file:
        out_file.write("{}\n".format(title))

        for line in contents:
            out_file.write("{}\n".format(line))


# find all the news in a page for bbc bangla only
def find_all_links(page):

    soup = BeautifulSoup(page, 'html.parser')
    # print(page)

    see_also_section = soup.find_all('div')
    # see_also_soup =  see_also_section.find_all('li')
    # print(see_also_soup)

    news_ids = []
    for li in see_also_section:
        try:
            a_tag = li.find('a', href=True, attrs={'title':False, 'class':True}) # find a tags that have a title and a class
            href = a_tag['href'] # get the href attribute

            isNews = href.strip().split('/')[-1]  #get only those links with 'news' in the end
            if isNews.split('-')[0] == 'news':
                # text = a_tag.getText() # get the short title of that news article
                news_ids.append(isNews) # append to array (we want only the news-number)
        except:
            # print('No Further <a> tag')
            pass
    
    news_ids = list(set(news_ids))
    # print(news_ids)
    return news_ids


# this function checks a url and returns the http.client.HTTPResponse object
def check_page_validity(url):
    # query the website and return the html to the variable ‘page’
    try:
        page = urllib.request.urlopen(url)
        return page
    except:
        print("An error occured.")
        return None


# this function processes a Base URL and returns possible subcategoes...
def process_news(base_url, news_ids):
    
    sub_categories = []

    for id in news_ids:
        url = base_url + '/' + id   # appending the news-# at the end of the base_url
        print(url)
        
        page = check_page_validity(url)    
        
        if page:
            title, contents = get_data(page)
            
            if contents:
                # calling the function to write the .text
                write_text_file(id, title, contents)

                # saving the PDF file of the Page - if you don't need PDF then comment/remove the code below
                # For Installation support of 'Weasyprint' visit the link below
                # Visit https://weasyprint.readthedocs.io/en/latest/install.html#step-1-install-python
                HTML(url).write_pdf('output/'+id+'.pdf')
            else:
                # these might be the subcategories of news (like Sports/Politics... etc)
                sub_categories.append(id)

    # removing duplicate elements
    sub_categories = list(set(sub_categories))
    # print(sub_categories)
    return sub_categories


def level_of_depth(base_url, sub_categories, depth):

    if depth == 0:
        return 0

    # each call tries to process subcategoes from previous level of depth...
    print('\n\n### Processing News Subcategories of Depth {} ###\n'.format(depth))
    for sub_page in sub_categories:
        # get all the news id in that page
        print('## Getting All the News For Subpage = ',sub_page)
        page = check_page_validity(base_url+'/'+sub_page)
        news_ids = find_all_links(page)
        sub_categories = process_news(base_url, news_ids)
    
    # recursively calling this function to go into further depth (subcategories of news)
    level_of_depth(base_url, sub_categories, depth-1)


# This function mainly process first level (Base URL) of news (if any). 
def main(depth):
    # specify the base url with many news links and possible subcategories
    base_url = 'https://www.bbc.com/bengali'

    # get all the news id in that page
    page = check_page_validity(base_url)
    news_ids = find_all_links(page)

    # first call is to process the base url and to get all possible subcategories (like Sports/Politics... etc)
    sub_categories = process_news(base_url, news_ids)
    
    # Going into depth to process further news subcategories (if depth > 1)
    level_of_depth(base_url, sub_categories, depth-1)


# starts program from here...
if __name__ == "__main__":
    depth = int(input('How many levels of News subcategories Do you want to Crawl?\nDefault is 1: '))
    
    if depth < 1:
        depth = 1

    main(depth)

    