#!/usr/bin/python
from sys import argv
import os
import base64
import zbar
import Image
import re
from urllib2 import urlopen
from urllib2 import Request

# Select route
QR_url = 'http://freess.cx/images/servers/jp02.png' #default
QR_list = [
'http://freess.cx/images/servers/jp01.png',
'http://freess.cx/images/servers/jp02.png',
'http://freess.cx/images/servers/jp03.png',
'http://freess.cx/images/servers/us01.png',
'http://freess.cx/images/servers/us02.png',
'http://freess.cx/images/servers/us03.png',
]
i = 1
for item in QR_list:
    print item,'#',i 
    i += 1
s = input('Please select the route YOU WANT!(1-6):')
if s > 0 and s < 7:
    QR_url = QR_list[s-1]
else:
    exit

headers={
#'Host':host,#domain and others header
'User-Agent':'Mozilla/5.0 (Windows NT 6.2; rv:16.0) Gecko/20100101 Firefox/16.0',
'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
'Connection':'keep-alive'
}
req = Request(QR_url,headers=headers)
req.get_method=lambda: 'HEAD'
img_file = urlopen(req)
# create a reader
scanner = zbar.ImageScanner()
# configure the reader
scanner.parse_config('enable')
#obtain image data
pil=Image.open(img_file).convert('RGBA').convert('L')
width, height = pil.size
raw = pil.tobytes()  
# wrap image data  
image = zbar.Image(width, height, 'Y800', raw)  
# scan the image for barcodes  
scanner.scan(image)  
# extract results  
for symbol in image:  
    # do something useful with results  
    #print 'QR decoded', symbol.type, 'symbol', '"%s"' % symbol.data  
    pass
  
# decode the  base64 strings 's://YMdfseI232-----'
base64_str = symbol.data[5:]
base64_dstr = base64.standard_b64decode(base64_str)

print base64_dstr
# display the shadowsocks server info
# example:'aes-256-cfb:34168121@139.162.67.43:443\n'
r = re.compile('(.*):(\d*)@(.*):(\d*)\n')
r_res = re.match(r,base64_dstr)
#r_res = re.match('(.*):(\d*)@([\d\.]*):(\d*)\n',base64_dstr)

ss_info = {'method':None,'server-ip':None,'port':None,'pass':None}
ss_info['method'] = r_res.group(1)
ss_info['server-ip'] = r_res.group(3)
ss_info['port'] = r_res.group(4)
ss_info['pass'] = r_res.group(2)


print '--Get info from--\n',QR_url
print '--Decoded QR & Base64 result--\n',base64_dstr
print '---------------------------------'
print '|server-ip:',ss_info['server-ip'],'	|'
print '|server-port:',ss_info['port'],'		|'
print '|password:',ss_info['pass'],'		|'
print '|method:',ss_info['method'],'		|'
print '---------------------------------'

# start shadowsocks client
#sslocal -s 139.162.67.43 -p 443 -k 34168121
ss_cmd = 'sslocal -s %s -p %s -k %s'%(ss_info['server-ip'],ss_info['port'],ss_info['pass'])
print '\n\n############start shadowsocks client#########\n'
print ss_cmd
os.system(ss_cmd)

# clean up  
del(image)  


#freess website 'http://freess.org/',not stable
#also you can use 'shadowsocks-qt5'
#You may need 'genpac' to get a pac file for brower!!


