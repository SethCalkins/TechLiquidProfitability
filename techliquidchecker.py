import sys
if sys.version_info<(3,4,0):
  sys.stderr.write("You need python 3.4 or later to run this script\n")
  exit(1)

from bs4 import BeautifulSoup
import urllib.request
import csv

ans = True
numfail = 0
count = 0
revenue = 0
profit = 0
auctionname = ''
currentbid = ''
quantity = 0
name = 0
msrp = 0
marketprice = 0
itemrevenue = 0
auctionrevenue = 0
profit = 0
listingurl = 0
count = 0
numfail = 0
prevlink = 0

mainlink = urllib.request.urlopen('http://techliquidators.com/index.cfm?p=4&sorttype=11&categories=0&sizes=1&condition=0&location=0&vhr=&vhi=&bc=1&maxrows=100')
mainlink = BeautifulSoup(mainlink)

def pageparser():
    global numfail
    global count
    global prevlink
    prevlink = 0
    numsucc = 0

    csvprint('Auction Name', 'Current Bid', 'Quantity','Product','MSRP','Market', 'Revenue', 'Auction Revenue', 'Profit' , 'Auction Link', 'Market Link')

    for link in mainlink.find_all('a'): #finds all links
        if ((str(link.get('href'))).find('index.cfm/p/34')) != -1 and link.get('href') != prevlink: ##makes sure it fits criteria, then does all that
            
            prevlink = link.get('href')
            pricelookup(prevlink, 0)

                    ##              Auction Name',      'Current Bid',   'Quantity',  'Product',  'MSRP',        Market',     'Revenue',          'Auction Revenue',          'Profit', '', 'Auction Link', 'Market Link'])
            csvprint('','','','','','','','','','','')##blank seperation row

    stats(count, numfail, 0, 0)

def pricelookup(link, option):
    global numfail
    global count
    global auctionname
    global currentbid
    global quantity
    global name
    global msrp
    global marketprice
    global itemrevenue
    global auctionrevenue
    global profit
    global listingurl

    man_doc=urllib.request.urlopen(link)
    man = BeautifulSoup(man_doc)##downloads this listing

    auctionname = man.title
    auctionname = str(auctionname)[7:len(auctionname) - 9] ##finds the auction name
    auctionname = str(auctionname).replace('&amp;', '+').replace(';','')
    
    currentbid = str(man)[str(man).find('Current Bid:') + 170:str(man).find('Current Bid:') + 180]
    currentbid = str(currentbid).replace(',','').replace(' ','')
    print('\nAuction: ' + str(auctionname) + ' Current Bid: ' + str(currentbid))

    manifest = str(man)[str(man).find('id="urlManifestHTM"') + 63:]##extracts manifest link
    manifest = str(manifest)[:str(manifest).find('.htm') + 4]
    manifest_trimmed = 'http://techliquidators.com' + str(manifest) ## finalizes manifest link

    manifest_downloaded = urllib.request.urlopen(manifest_trimmed)
    manifest_downloaded = BeautifulSoup(manifest_downloaded) ##download and put into beautiful soup the manifest
    manifest_downloaded.prettify()
    manifest_extract = manifest_downloaded.find_all('td')
    manifest_extract = str(manifest_extract)[str(manifest_extract).find('Total MSRP') + 17:] ##delete preliminary info

    auctionrevenue = 0 ##reset auction revenue
    profit = 0
    while(str(manifest_extract).startswith('<td></td>') == False): ##Loops through and extracts the information from the manifest
        count += 1
        itemrevenue = 0 ##reset item revenue

        quantity = str(manifest_extract)[4:str(manifest_extract).find('>, ') - 4]
        manifest_extract = str(manifest_extract)[str(manifest_extract).find('>,') + 3:]
        manifest_extract = str(manifest_extract)[str(manifest_extract).find('>,') + 3:]

        partnum = str(manifest_extract)[4:str(manifest_extract).find('>, ') - 4]

        manifest_extract = str(manifest_extract)[str(manifest_extract).find('>,') + 3:]

        name = str(manifest_extract)[4:str(manifest_extract).find('>, ') - 4] ## prints the listing name
        name = str(name).replace('AT&amp;T', 'ATT').replace(';', ' ')

        manifest_extract = str(manifest_extract)[str(manifest_extract).find('>,') + 3:]
        manifest_extract = str(manifest_extract)[str(manifest_extract).find('>,') + 3:]
        manifest_extract = str(manifest_extract)[str(manifest_extract).find('>,') + 3:]

        msrp = str(manifest_extract)[4:str(manifest_extract).find('>, ') - 4] ##then the price

        manifest_extract = str(manifest_extract)[str(manifest_extract).find('>,') + 3:]
        manifest_extract = str(manifest_extract)[str(manifest_extract).find('>,') + 3:]
        
        ##wall of replacements
        itemname = name.lower()
        itemname = str(itemname).replace('-', '+').replace('at&amp;t;', 'att').replace('"', '+').replace('feat.', '+').replace('/', '+').replace(' ', '+').replace('-bl','').replace('-wh','')
        
        if 'ipad' in str(itemname):
            itemname = str(itemname)[str(itemname).find('ipad'):] ##deletes model number prefix
        if 'intel' in str(itemname) or 'amd' in str(itemname):
            itemname = str(partnum) ##if a laptop, the part number is used instead of item name
        try:
            listingurl = ('http://www.thepricegeek.com/results/' + str(itemname) + '?country=us')
            marketprice = BeautifulSoup(urllib.request.urlopen(listingurl))
            marketprice = str(marketprice.find_all(class_="median"))
            marketprice = str(marketprice)[20:len(str(marketprice)) - 4]
            marketprice = str(marketprice).replace('$','').replace('<','').replace('/','').replace(',','') ##clean up price

            if(str(marketprice) == ''):
                marketprice = 'NOTFOUND'
                numfail +=1
        except urllib.error.HTTPError:
            marketprice = 'HTTPERROR'
            numfail +=1
        except UnicodeEncodeError:
            marketprice = 'HTTPERROR'
            numfail += 1
        except urllib.error.URLError:
            marketprice = 'HTTPERROR'
            numfail +=1
        try:
            ##if(str(marketprice) != 'NOTFOUND' and str(marketprice) != 'HTTPERROR'): GET THIS TO WORK
            itemrevenue = int(quantity) * float(marketprice)
            auctionrevenue = auctionrevenue + itemrevenue
            profit = auctionrevenue - float(currentbid) ## plus auctionrevenu
        except ValueError:
            pass
        

        print('Quantity: ' + str(quantity) + ' Product: ' + str(name) + ' MSRP: ' + str(msrp) + ' Market: ' + str(marketprice))
        csvprint(auctionname, float(currentbid), quantity, name, msrp, marketprice, itemrevenue, auctionrevenue, profit, prevlink, listingurl)
           
        if(option == 1):
            stats(count, numfail, auctionrevenue, profit)

def stats(count, numfail, revenue, profit):
    if(revenue == 0 or profit == 0):
        print('\nStats:\nCheck Output for More Details\nNumber of Failed Searches: ' + str(numfail) + ' Total Searches: ' + str(count))
    else:
        print('\nStats:\nNumber of Failed Searches: ' + str(numfail) + ' Number of Searches: ' + str(count) + ' Total Revenue: ' + str(revenue) + ' Profit: ' + "%.2f" % float(profit))

def csvprint(auctionname, currentbid, quantity, name, msrp, marketprice, itemrevenue, auctionrevenue, profit, link, marketlink):
        csvwriter.writerow([str(auctionname), str(currentbid),str(quantity), str(name), str(msrp), str(marketprice), str(itemrevenue),   str(auctionrevenue), str(profit), '' , str(link), str(marketlink)])



while ans:
    print ("""
    1.Run Small Quantity Parser
    2.Enter a link to determine profitability
    "q" to quit
    """)
    ans=input("What would you like to do? ") 
    if ans=="1": 
      print("\nRunning")
      with open('output.csv', 'w', newline='') as csvfile: ##opens output.csv as a writable file
          csvwriter = csv.writer(csvfile, dialect='excel')
          pageparser()
          stats(count, numfail, 0, 0)
    elif ans=="2":
      link = input("\nEnter TechLiquid Auction Link: ")
      pricelookup(link, 1)
    elif ans=="q":
        break
    elif ans !="":
      print("\nNot Valid Choice Try again") 