# TripAdvisor Analysis

## About The Project

This repository offers some easy to use functions to scrape and analyze publicly available reviews on Tripadvisor.
The Review Analysis methods in NLP_Functions.py somewhat follows the methods described in "Opinion mining from online hotel reviews – A text summarization approach" (https://doi.org/10.1016/j.ipm.2016.12.002)


## Built With

* [Selenium](https://selenium-python.readthedocs.io/)
* [NLTK](https://www.nltk.org/)
* [SciLearn](https://scikit-learn.org/stable/)
* [Sentence Transformers](https://www.sbert.net/)
* [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
* [Pandas](https://pandas.pydata.org/)

## Getting Started

Clone this repo and ensure that all dependencies are installed.

### Dependencies
* beautifulsoup4 4.10.0
* lxml 4.6.4
* nltk 3.7
* numpy 1.21.4
* pandas 1.3.4
* scikit-learn-extra 0.2.0
* selenium 4.0.0
* sentence-transformers 2.2.0

The appropriate chromedriver (https://chromedriver.chromium.org/downloads) must be downloaded and configured in the PATH.
This page (https://www.selenium.dev/documentation/webdriver/getting_started/install_drivers/) can be useful for setting up the chromedriver

You should now be able to run the modules in your Python environment

## Overview of Modules

### Scrape_Data

#### scrapeData
The scrapeData function is used to scrape reviews off of the TripAdvisor website and store the data in an Excel Spreadsheet. All TripAdvisor links follow the standard form "https://tripadvisor.com<Something\>-or\<number\>-\<Comapany\>". 

##### Parameters
* linkFront is a string including the beginning of the link including the "or"
* linkBack is a string including the end of the review including "-\<Company\>"
* rangeLow is an int corresponding to the first review that you want begin to scrape (must be a multiple of 5 and at least 5)
* rangeHigh is an int corresponding to the last review that you want to scrape (must be a multiple of 5 and at least 5)
* name is the name of the Excel file that is created

Should the driver fail during the scraping process, the review data will be automatically saved to an Excel file and the process will be terminated

#### concatenate
The concatenate function merges two review data spreadsheets (Useful if scraping process terminated prematurely).

##### Parameters
* name is the name of your Excel file
* sheets is a list of Excel spreadsheets to concatenate

### NLP_Functions
The only function designed for use is Run_Analysis.

#### Run_Analysis
Analyzes a set of reviews scraped off of TripAdvisor using the Scrape_Data module. Returns the k most important sentences in the entire review set from p clusters. This methodology follows from the review article mentioned above.

##### Parameters
* data_set is the name of the Excel spreadsheet that contains the review data
* num_reviews is the number of reviews that you want to analyze from that dataset
* num_clusters is the number of clusters you want to create from the reveiw set
* sentences_per_cluster is the top k important sentences that you want to extract from each cluster
* W1, W2, and W3 are weights for determining the importance of sentences as described in the research article
* excel determines whether the analysis is exported as an excel spreadsheet for easier viewing



## Contributors/Contact
* Adam Horton - adam.horton@ufl.edu

Project Link: [https://github.com/adam-horton/TripAdvisor_Analysis](https://github.com/adam-horton/TripAdvisor_Analysis)