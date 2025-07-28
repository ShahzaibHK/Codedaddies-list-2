import requests
from requests.compat import quote_plus
from django.shortcuts import render
from bs4 import BeautifulSoup
from . import models

BASE_CRAIGSLIST_URL = 'https://losangeles.craigslist.org/search/sss?query={}'

# Create your views here.
def home(request):
    return render(request,'base.html')

def new_search(request):
    search= request.POST.get('search')
    models.Search.objects.create(search=search)  # Save the search term to the database

    final_url = BASE_CRAIGSLIST_URL.format(quote_plus(search))
    response=requests.get(final_url)
    data = response.text
    soup = BeautifulSoup(data, features='html.parser')
    post_listings = soup.find_all('li', {'class': 'cl-static-search-result'},limit=5)
    
    
    final_postings = []

    for post in post_listings[::2]:
        post_title = post.find(class_='title').text
        post_url = post.find('a').get('href')
        post_image_url = 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQb7CPgEDcE4g1wG5pEiBuk9Z3nf1LcoxB0oQ&s'

        if post.find(class_='price'):
            post_price = post.find(class_='price').text
        else:
            post_price = 'N/A'
        
        image_response=requests.get(post_url)
        data = image_response.text
        soup = BeautifulSoup(data, features='html.parser')
        post_image_listings = soup.find_all('img')
        if post_image_listings:
            post_image_url = post_image_listings[0].get('src')
        final_postings.append((post_title, post_url, post_price,post_image_url))
        
    stuff_for_frontend ={
        'search': search,
        'final_postings': final_postings,
        'total_results': len(final_postings),
        'search_history': models.Search.objects.all().order_by('-id')[:5]

    }
    return render(request,'main/new_search.html',stuff_for_frontend)