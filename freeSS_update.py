#!/usr/bin/python
from sys import argv
import os
import base64
import zbar
from PIL import Image
import re
from urllib2 import urlopen
from urllib2 import Request
import time
import signal
import traceback

def select_route(QR_url_base='http://www.freess.vip/assets/'):
    # Select route
    QR_url = QR_url_base + 'jp02.png' #default
    QR_list = [
    QR_url_base + 'jp01.png',
    QR_url_base + 'jp02.png',
    QR_url_base + 'jp03.png',
    QR_url_base + 'us01.png',
    QR_url_base + 'us02.png',
    QR_url_base + 'us03.png',
    ]
    i = 1
    for item in QR_list:
        print item,'#',i
        i += 1
    s = input('Please select the route YOU WANT!(1-6):')
    if s == 0:
        QR_url = input('Enter your ss QR url:')
    elif s > 0 and s < 7:
        QR_url = QR_list[s-1]
    else:
        pass

    return QR_url

def resolve_ssurl(QR_url):
    '''
    headers = {
    #'Host':host,#domain and others header
    'User-Agent':'Mozilla/5.0 (Windows NT 6.2; rv:16.0) Gecko/20100101 Firefox/16.0',
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Connection':'keep-alive'
    }
    req = Request(QR_url,headers=headers)
    req.get_method=lambda: 'HEAD'
    img_file = urlopen(req)
    '''
    img_file = urlopen(QR_url)
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

    # clean up
    del(image)
    return base64_dstr



def ss_connect(base64_dstr):
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

    print '--Decoded QR & Base64 result--\n',base64_dstr
    print '---------------------------------'
    print '|server-ip:',ss_info['server-ip'],'	|'
    print '|server-port:',ss_info['port'],'		|'
    print '|password:',ss_info['pass'],'		|'
    print '|method:',ss_info['method'],'		|'
    print '---------------------------------'

    # start shadowsocks client
    #sslocal -s 139.162.67.43 -p 443 -k 34168121
    #ss_cmd = 'sslocal  -s %s -p %s -k %s'%(ss_info['server-ip'],ss_info['port'],ss_info['pass'])
    ss_cmd = 'sslocal  -s %s -p %s -k %s'%(ss_info['server-ip'],ss_info['port'],ss_info['pass'])
    print '\n\n############start shadowsocks client#########\n'
    print ss_cmd
    #os.system(ss_cmd)
    #os.exit(0)

    args =  ss_cmd.split()
    os.execlp(args[0],args[0],*args[1:])

def main_task():
    QR_url = ""
    base64_dstr = ""
    base64_dstr_old = ""
    child_pid = 0

    QR_url = select_route(QR_url_base='http://www.freess.vip/assets/')
    while True:
        try:
            base64_dstr = resolve_ssurl(QR_url)
            if base64_dstr != base64_dstr_old:
                print "ss url change -- "
                if child_pid > 0:
                    print "kill child_pid: %s" % child_pid
                    #os.kill(child_pid,signal.SIGINT)
                    os.kill(child_pid,signal.SIGKILL)
                    os.wait() #wait for child release sources
                    time.sleep(1)
                pid = os.fork()
                if pid == 0:
                    print "child process - %s" % os.getpid()
                    ss_connect(base64_dstr)
                else:
                    print "parent process"
                    child_pid = pid
                    base64_dstr_old = base64_dstr
        except Exception:
            traceback.print_exc()

        time.sleep(30)
        #test
        #base64_dstr_old = ""


if __name__ == "__main__":
    main_task()



#freess website 'http://freess.org/',not stable
#also you can use 'shadowsocks-qt5'
#You may need 'genpac' to get a pac file for brower!!
