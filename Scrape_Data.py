from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd

def scrapeData(linkFront, linkBack, rangeLow, rangeHigh, name):
    #initialize webdriver
    chromeOptions = Options()
    chromeOptions.headless = True #Does not open page every time
    chromeOptions.add_argument("--log-level=3") #Does not print to console
    driver = webdriver.Chrome(options=chromeOptions)

    reviews = []
    starRatings = []
    titles = []
    monthOfTravel = []
    yearOfTravel = []
    author = []
    authorContributionsAllTime = []
    authorHelpfulVotesAllTime = []
    reviewHelpfulVotes = []
    legroom = []
    entertainment = []
    vfm = []
    checkin = []
    seatComf = []
    customerServ = []
    cleanliness = []
    foodAndDrink = []

    monthMap = {
                'Jan' : 1,
                'Feb' : 2,
                'Mar' : 3,
                'Apr' : 4,
                'May' : 5,
                'Jun' : 6,
                'Jul' : 7,
                'Aug' : 8,
                'Sep' : 9,
                'Oct' : 10,
                'Nov' : 11,
                'Dec' : 12
                }

    extraInfo = {
                 'Legroom' : legroom,
                 'In-flight_Entertainment' : entertainment,
                 'Value_for_money' : vfm,
                 'Check-in_and_boarding' : checkin,
                 'Seat_comfort' : seatComf,
                 'Customer_service' : customerServ,
                 'Cleanliness' : cleanliness,
                 'Food_and_Beverage' : foodAndDrink
                 }

    tableDict = {
             'Title' : titles,
             'Review' : reviews,
             'Stars' : starRatings,
             'Month' : monthOfTravel,
             'Year' : yearOfTravel,
             'Author' : author,
             'Author_Contributions_All_Time' : authorContributionsAllTime,
             'Author_Helpful_Votes_All_Time' : authorHelpfulVotesAllTime,
             'Review_Helpful_Votes' : reviewHelpfulVotes,
             'Legroom' : legroom,
             'In-flight_Entertainment' : entertainment,
             'Value_for_ money' : vfm,
             'Check-in_and_boarding' : checkin,
             'Seat_comfort' : seatComf,
             'Customer_service' : customerServ,
             'Cleanliness' : cleanliness,
             'Food_and_Beverage' : foodAndDrink
             }

    for i in range(rangeLow, rangeHigh, 5):            
        #print an update every 100 reviews
        if i % 100 == 0:
           print(i)

        #Load the page
        while(True):
            try:
                driver.get(linkFront + str(i) + linkBack)
                break
            except:
                print('Load Page ', i, ' Failed... Giving Up')
                driver.quit()
                dataFrame = pd.DataFrame(tableDict)
                tempName = name + str(rangeLow) + '-' + str(i) + '.xlsx'
                dataFrame.to_excel(tempName)
                driver.quit()
                return
        

        #Click the "Read more" button to get the full text of each review
        driver.implicitly_wait(1)
        failCounter = 0
        while(True):
            try:
                showmorebutton = driver.find_element(By.CLASS_NAME, 'dlJyA')
                showmorebutton.click()
                break
            except:
                failCounter += 1
                driver.implicitly_wait(.5)
                if failCounter == 10:
                    print('Driver Failed on ', i, '... Giving Up')
                    dataFrame = pd.DataFrame(tableDict)
                    tempName = name + str(rangeLow) + '-' + str(i) + '.xlsx'
                    dataFrame.to_excel(tempName)
                    driver.quit()
                    return

        #Convert the HTML of the page to a BS object for easier scraping
        page_source = driver.page_source
    
        soup = BeautifulSoup(page_source, 'lxml')

        #Scrape the review text from all 5 reviews
        for comment in soup.find_all('q', class_="XllAv H4 _a"):
            reviews.append(comment.get_text())

        #Scrape the star rating from all 5 reviews
        for reviewVal in soup.find_all('div', class_='emWez F1'):
            starRatingString = reviewVal.contents[0]['class'][1]
            starRating = int(starRatingString[7:8])
            starRatings.append(starRating)

        #Scrape the title from each of the 5 reviews
        for title in soup.find_all('div', class_='fpMxB MC _S b S6 H5 _a'):
            titles.append(title.get_text())

        #Scrape the date and username from each of the 5 reviews
        for dateOfTravel in soup.find_all('div', class_='bcaHz'):
            dateString = dateOfTravel.get_text()
            if len(dateString) != 0:
                if dateString[len(dateString)-15:len(dateString)-9] == 'review':
                    yearOfTravel.append(int(dateString[len(dateString)-4:]))
                    monthOfTravel.append(monthMap[dateString[len(dateString)-8:len(dateString)-5]])
                    author.append(dateString[0:len(dateString)-24])
                    
                elif dateString[len(dateString)-12:len(dateString)-6] == 'review':
                    yearOfTravel.append(2022)
                    monthOfTravel.append(monthMap[dateString[len(dateString)-5:len(dateString)-2]])
                    author.append(dateString[0:len(dateString)-21])

                elif dateString[len(dateString)-13:len(dateString)-7] == 'review':
                    yearOfTravel.append(2022)
                    monthOfTravel.append(monthMap[dateString[len(dateString)-6:len(dateString)-3]])
                    author.append(dateString[0:len(dateString)-22])

                elif dateString[len(dateString)-16:len(dateString)-10] == 'review':
                    yearOfTravel.append(2022)
                    monthOfTravel.append(2)
                    author.append(dateString[0:len(dateString)-25])

        #Extract an author's all time contributions and helpful votes
        for numContributions in soup.find_all('div', class_='BZmsN'):
            authorStats = numContributions.find_all('span', class_='ckXjS')

            if len(authorStats) == 0:
                continue
            
            #Scrape the author's number of contributions to Tripadvisor
            
            authorContributionsAllTime.append(int(authorStats[0].get_text()))

            #If available, scrape the number of helpful votes the author has received
            if len(authorStats) == 2:
                authorHelpfulVotesAllTime.append(int(authorStats[1].get_text()))
            else:
                authorHelpfulVotesAllTime.append(0)

        #Scrape the number of helpful votes received by the review
        for comment in soup.find_all('div', class_='euJzb'):
            helpfulVotes = comment.find_all('span', class_='ekLsQ S2 H2 Ch bzShB')
            if len(helpfulVotes) == 0:
                reviewHelpfulVotes.append(0)
            else:
                words = helpfulVotes[0].get_text().split(' ')
                reviewHelpfulVotes.append(int(words[0]))

        #Scrape the extra star data if available            
        currentCount = len(reviews) - 5
        for extraData in soup.find_all('div', class_='dovOW'):
            currentCount += 1

            #For each extraDataPoint available, place it in the appropriate list
            for dataPoint in extraData.contents[2].contents:
                if dataPoint.get_text() in extraInfo:
                    ratingString = dataPoint.contents[0].contents[0]['class'][1]
                    extraInfo[dataPoint.get_text()].append(int(ratingString[7:8]))
                    
            for extraInfoList in extraInfo.values(): #if an extra data point could not be found, fill it with a "?"
                if len(extraInfoList) != currentCount:
                    extraInfoList.append('?')
                    

    tempName = name + str(rangeLow) + '-' + str(rangeHigh) + '.xlsx'
    dataFrame = pd.DataFrame(tableDict)
    dataFrame.to_excel(tempName)

    driver.quit()

if __name__ == "__main__":
    scrapeData('https://tripadvisor.com/Airline_Review-d8729156-Reviews-or', '-Southwest-Airlines', 5, 10, 'tester')
