from django.shortcuts import render

# Create your views here.
from bs4 import BeautifulSoup
import requests

def home(request):
    url = 'https://www.meesho.com/'
    
    text = requests.get(url).text
    
    
    # data = 
    return render(request,'home.html')  

def scrapedsites(request):
    return render(request,'scrapedsites.html')

def contact(request):
    return render(request,'contact.html')


def show(request):
    response = requests.get('https://www.amazon.in/s?k=laptop+under+35000&crid=X49UIOPFC5MY&sprefix=laptop%2Caps%2C321&ref=nb_sb_ss_mvt-t11-ranker_1_6').text
    
    print(response)
    
    # soup = BeautifulSoup(response,'html-parser')
    
    # data = soup.find_all('')
    
    return render(request,'show.html')