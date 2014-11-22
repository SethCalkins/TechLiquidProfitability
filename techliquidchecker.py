from bs4 import BeautifulSoup
import urllib.request

html_doc = urllib.request.urlopen('http://techliquidators.com/index.cfm?p=4&sorttype=11&categories=0&sizes=1&condition=0&location=0&vhr=&vhi=&bc=1&maxrows=100')
soup = BeautifulSoup(html_doc)
count = 1
prevlink = 0

for link in soup.find_all('a'): #finds all links
    if ((str(link.get('href'))).find('index.cfm/p/34')) != -1 and link.get('href') != prevlink: ##makes sure it fits criteria, then does all that
        prevlink = link.get('href')
        
        man_doc=urllib.request.urlopen(link.get('href'))
        man = BeautifulSoup(man_doc)##downloads this listing

        currentbid = str(man)[str(man).find('Current Bid:'):]
        currentbid = str(currentbid)[str(currentbid).find('Current Bid:') + 170:str(currentbid).find('Current Bid:') + 176]
        
        manifest = str(man)[str(man).find('name="urlManifestHTM" type="hidden" value="'):str(man).find('.htm">',str(man).find('name="urlManifestHTM" type="hidden" value="'))]##extracts manifest link
        manifest_trimmed = 'http://techliquidators.com' + str(manifest)[str(manifest).find('/'):] + '.htm' ## finalizes manifest link
        
        print ('\n' + str(count) + ". " + str(manifest_trimmed)) ##lists link with numbers
        count = count + 1
        print ('Current Bid: ' + str(currentbid))

        manifest_downloaded = BeautifulSoup(urllib.request.urlopen(manifest_trimmed)) ##download and put into beautiful soup the manifest
        manifest_downloaded.prettify()
        manifest_extract = manifest_downloaded.find_all('td')

        manifest_extract = str(manifest_extract)[str(manifest_extract).find('Total MSRP') + 17:] ##delete preliminary info

        ##print(manifest_extract)
        
        while(str(manifest_extract).startswith('<td></td>') == False):

            quantity = str(manifest_extract)[4:str(manifest_extract).find('>, ') - 4]
            manifest_extract = str(manifest_extract)[str(manifest_extract).find('>,') + 3:]
            manifest_extract = str(manifest_extract)[str(manifest_extract).find('>,') + 3:]
            manifest_extract = str(manifest_extract)[str(manifest_extract).find('>,') + 3:]

            name = str(manifest_extract)[4:str(manifest_extract).find('>, ') - 4] ## prints the listing name

            manifest_extract = str(manifest_extract)[str(manifest_extract).find('>,') + 3:]
            manifest_extract = str(manifest_extract)[str(manifest_extract).find('>,') + 3:]
            manifest_extract = str(manifest_extract)[str(manifest_extract).find('>,') + 3:]

            msrp = str(manifest_extract)[4:str(manifest_extract).find('>, ') - 4] ##then the price

            manifest_extract = str(manifest_extract)[str(manifest_extract).find('>,') + 3:]
            manifest_extract = str(manifest_extract)[str(manifest_extract).find('>,') + 3:]
            
            print('Quantity: ' + str(quantity) + ' Product: ' + str(name) + ' MSRP: ' + str(msrp))