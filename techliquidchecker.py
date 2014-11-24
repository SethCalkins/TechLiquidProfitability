from bs4 import BeautifulSoup
import urllib.request
import csv

html_doc = urllib.request.urlopen('http://techliquidators.com/index.cfm?p=4&sorttype=11&categories=0&sizes=1&condition=0&location=0&vhr=&vhi=&bc=1&maxrows=100')
soup = BeautifulSoup(html_doc)
count = 1
prevlink = 0

with open('output.csv', 'w', newline='') as csvfile: ##opens output.csv as a writable file
    csvwriter = csv.writer(csvfile, dialect='excel') ##CSVwriter as excel
    csvwriter.writerow(['Auction Name', 'Current Bid', 'Quantity','Product','MSRP','Market', 'Revenue', 'Auction Revenue', 'Profitability', '', 'Auction Link', 'Manifest Link']) ## makes headers
    for link in soup.find_all('a'): #finds all links
        if ((str(link.get('href'))).find('index.cfm/p/34')) != -1 and link.get('href') != prevlink: ##makes sure it fits criteria, then does all that
            prevlink = link.get('href')
            
            man_doc=urllib.request.urlopen(link.get('href'))
            man = BeautifulSoup(man_doc)##downloads this listing

            auctionname = man.title
            auctionname = str(auctionname)[7:len(auctionname) - 9] ##finds the auction name
            auctionname = str(auctionname).replace('&amp;', '+')
            auctionname = str(auctionname).replace(';','')
            ##currentbid = str(man)[str(man).find('Current Bid:'):]
            currentbid = str(man)[str(man).find('Current Bid:') + 170:str(man).find('Current Bid:') + 176]
           
            
            manifest = str(man)[str(man).find('name="urlManifestHTM" type="hidden" value="'):str(man).find('.htm">',str(man).find('name="urlManifestHTM" type="hidden" value="'))]##extracts manifest link
            manifest_trimmed = 'http://techliquidators.com' + str(manifest)[str(manifest).find('/'):] + '.htm' ## finalizes manifest link
            
            print ('\n' + str(count) + ". " + str(manifest_trimmed)) ##lists link with numbers
            count = count + 1
            print ('Current Bid: ' + str(currentbid))

            manifest_downloaded = BeautifulSoup(urllib.request.urlopen(manifest_trimmed)) ##download and put into beautiful soup the manifest
            manifest_downloaded.prettify()
            manifest_extract = manifest_downloaded.find_all('td')

            manifest_extract = str(manifest_extract)[str(manifest_extract).find('Total MSRP') + 17:] ##delete preliminary info

            
            while(str(manifest_extract).startswith('<td></td>') == False):

                quantity = str(manifest_extract)[4:str(manifest_extract).find('>, ') - 4]
                manifest_extract = str(manifest_extract)[str(manifest_extract).find('>,') + 3:]
                manifest_extract = str(manifest_extract)[str(manifest_extract).find('>,') + 3:]
                manifest_extract = str(manifest_extract)[str(manifest_extract).find('>,') + 3:]

                name = str(manifest_extract)[4:str(manifest_extract).find('>, ') - 4] ## prints the listing name
                name = str(name).replace('AT&amp;T', 'ATT')
                name = str(name).replace(';', ' ')

                manifest_extract = str(manifest_extract)[str(manifest_extract).find('>,') + 3:]
                manifest_extract = str(manifest_extract)[str(manifest_extract).find('>,') + 3:]
                manifest_extract = str(manifest_extract)[str(manifest_extract).find('>,') + 3:]

                msrp = str(manifest_extract)[4:str(manifest_extract).find('>, ') - 4] ##then the price

                manifest_extract = str(manifest_extract)[str(manifest_extract).find('>,') + 3:]
                manifest_extract = str(manifest_extract)[str(manifest_extract).find('>,') + 3:]
                
                ##wall of replacements
                itemname = name.lower()
                itemname = str(itemname).replace('-', '+')
                itemname = str(itemname).replace('at&amp;t;', 'att')
                itemname = str(itemname).replace('"', '+')
                itemname = str(itemname).replace('feat.', '+')
                itemname = str(itemname).replace('/', '+')
                itemname = str(itemname).replace(' ', '+')
                itemname = str(itemname)[str(itemname).find('ipad'):] ##deletes model number prefix
                try:
                    listingurl = ('http://www.thepricegeek.com/results/' + str(itemname) + '?country=us')
                    listingprice = BeautifulSoup(urllib.request.urlopen(listingurl))
                    listingprice = str((listingprice.find_all(class_="median")))[20:27]
                    if(str(listingprice) == ''):
                        listingprice = 'NOTFOUND'
                        ##print('http://www.thepricegeek.com/results/' + str(itemname) + '?country=us')
                except urllib.error.HTTPError:
                    listingprice = 'HTTPERROR'
                    ##print('http://www.thepricegeek.com/results/' + str(itemname) + '?country=us')
                except UnicodeEncodeError:
                    ##print('http://www.thepricegeek.com/results/' + str(itemname) + '?country=us')
                    break ##i dont know
                except urllib.error.URLError:
                    break
                
                

                print('Auction: ' + str(auctionname) + ' Quantity: ' + str(quantity) + ' Product: ' + str(name) + ' MSRP: ' + str(msrp) + ' Market: ' + str(listingprice))
                csvwriter.writerow([str(auctionname), str(currentbid),str(quantity), str(name), str(msrp), str(listingprice), 'TBD', 'TBD', 'TBD', '', str(prevlink), str(listingurl)])
print("\n\n Execution Complete")
