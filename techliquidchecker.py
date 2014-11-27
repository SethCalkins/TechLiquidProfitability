import sys
if sys.version_info<(3,4,0):
  sys.stderr.write("You need python 3.4 or later to run this script\n")
  exit(1)

from bs4 import BeautifulSoup
import urllib.request
import csv

mainlink = urllib.request.urlopen('http://techliquidators.com/index.cfm?p=4&sorttype=11&categories=0&sizes=1&condition=0&location=0&vhr=&vhi=&bc=1&maxrows=100')
mainlink = BeautifulSoup(mainlink)
count = 1
prevlink = ''

with open('output.csv', 'w', newline='') as csvfile: ##opens output.csv as a writable file
    csvwriter = csv.writer(csvfile, dialect='excel') ##CSVwriter as excel
    csvwriter.writerow(['Auction Name', 'Current Bid', 'Quantity','Product','MSRP','Market', 'Revenue', 'Auction Revenue', 'Profit', '', 'Auction Link', 'Market Link']) ## makes headers
    for link in mainlink.find_all('a'): #finds all links
        if ((str(link.get('href'))).find('index.cfm/p/34')) != -1 and link.get('href') != prevlink: ##makes sure it fits criteria, then does all that
            prevlink = link.get('href')
            
            man_doc=urllib.request.urlopen(link.get('href'))
            man = BeautifulSoup(man_doc)##downloads this listing

            auctionname = man.title
            auctionname = str(auctionname)[7:len(auctionname) - 9] ##finds the auction name
            auctionname = str(auctionname).replace('&amp;', '+')
            auctionname = str(auctionname).replace(';','')

            currentbid = str(man)[str(man).find('Current Bid:') + 170:str(man).find('Current Bid:') + 176]
            print ('\nCurrent Bid: ' + str(currentbid))

            manifest = str(man)[str(man).find('id="urlManifestHTM"') + 63:]##extracts manifest link
            manifest = str(manifest)[:str(manifest).find('.htm') + 4]
            manifest_trimmed = 'http://techliquidators.com' + str(manifest) ## finalizes manifest link

            count = count + 1

            manifest_downloaded = urllib.request.urlopen(manifest_trimmed)
            manifest_downloaded = BeautifulSoup(manifest_downloaded) ##download and put into beautiful soup the manifest
            manifest_downloaded.prettify()
            manifest_extract = manifest_downloaded.find_all('td')
            manifest_extract = str(manifest_extract)[str(manifest_extract).find('Total MSRP') + 17:] ##delete preliminary info

            auctionrevenue = 0 ##reset auction revenue
            profit = 0
            while(str(manifest_extract).startswith('<td></td>') == False): ##Loops through and extracts the information from the manifest
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
                itemname = str(itemname).replace('-', '+').replace('at&amp;t;', 'att').replace('"', '+').replace('feat.', '+').replace('/', '+').replace(' ', '+')
                if 'ipad' in str(itemname):
                    itemname = str(itemname)[str(itemname).find('ipad'):] ##deletes model number prefix
                if 'intel core' in str(itemname) or 'amd' in str(itemname):
                    itemname = str(partnum) ##if a laptop, the part number is used instead of item name
                try:
                    listingurl = ('http://www.thepricegeek.com/results/' + str(itemname) + '?country=us')
                    marketprice = BeautifulSoup(urllib.request.urlopen(listingurl))
                    marketprice = str((marketprice.find_all(class_="median")))[20:27]
                    marketprice = str(marketprice).replace('$','').replace('<','').replace('/','') ##clean up price

                    if(str(marketprice) == ''):
                        marketprice = 'NOTFOUND'
                except urllib.error.HTTPError:
                    marketprice = 'HTTPERROR'
                except UnicodeEncodeError:
                    marketprice = 'HTTPERROR'
                except urllib.error.URLError:
                    marketprice = 'HTTPERROR'
                try:
                    if(marketprice != 'NOTFOUND' and marketprice != 'NOTFOUND'):
                        itemrevenue = int(quantity) * float(marketprice)
                        auctionrevenue = auctionrevenue + itemrevenue
                        profit = auctionrevenue - int(currentbid) + 2
                except ValueError:
                    print('Error')
                

                print('Auction: ' + str(auctionname) + ' Quantity: ' + str(quantity) + ' Product: ' + str(name) + ' MSRP: ' + str(msrp) + ' Market: ' + str(marketprice))
                ##                  Auction Name',      'Current Bid',   'Quantity',  'Product',  'MSRP',        Market',     'Revenue',          'Auction Revenue',          'Profit', '', 'Auction Link', 'Market Link'])
                csvwriter.writerow([str(auctionname), str(currentbid),str(quantity), str(name),    str(msrp), str(marketprice), str(itemrevenue),   str(auctionrevenue),       str(profit),     '' , str(prevlink), str(listingurl)])
            csvwriter.writerow(['','','','','','','','','','','',''])##blank seperation row

print("\n\n Execution Complete")
input("Press Enter to continue...")
