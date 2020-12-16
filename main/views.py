from django.shortcuts import render
from .utils import contexts

# Create your views here.
# Mobility trackers, restaurant reservations among key figures


# alternative data streams
    # reddit stream of posts based on ticker
    # reddit sentiment analysis based on machine learning
    
# options and equities flow by ticker compared to mentions number on reddit

# TSA flight data 

# eod reports that are equities and fixed income 
def market_eod_report(request):
    charts_context = contexts.get_charts_context()
    # reddit_context = contexts.get_reddit_context()
    return render(request, 'eodreport/eodreport.html', charts_context)

