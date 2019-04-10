#!/usr/bin/python
from lxml import etree
import argparse, requests, sys, re

class OcadoClient:

  userid    = None
  sessionid = '8BFF9C71-CA91-4BA5-BE99-605806AEE64F'
  deviceid  = '8d8c124b51fe43eb'
  authtoken = '861e3a4f4da0819608f4c928da0274f6'
  useragent = 'Ocado-Android-Application/1.55.11'
  host      = 'mobile.ocado.com'

  def __init__( self, username, password ):
    self.login( username, password )

  def do_request( self, path, method='GET', data=None, headers=None, responseformat='json' ):
    url = 'https://' + self.host + path
    hdrs = {
      'User-Agent': self.useragent,
      'sessionId': self.sessionid,
      'Authorization': 'token:' + self.authtoken,
      'Accept': 'application/json,*/*'
    }
    if headers: hdrs.update( headers )
    if data: hdrs['Content-Length'] = str(len(str(data)))
    response = requests.request( method, url, data=data, headers=hdrs )
    # print re.sub(r'[^\x00-\x7F]+',' ', response.text )
    if not str( response.status_code ).startswith('2'):
      print response.text
      return False

    if responseformat == 'json':
      return response.json()

    if responseformat == 'xml':
      return etree.fromstring( response.text )

  def login( self, username, password ):
    rsp = self.do_request( '/webservices/mobileDevice/' + self.deviceid, 'POST', 
      {
        'username': username,
        'password': password
      }
    )
    if not rsp:
      return False
    self.authtoken = rsp['token']
    self.userid    = rsp['customerNo']
  
  def get_last_orderid( self ):
    rlt = self.do_request( '/webservices/user/'+str( self.userid )+'/orders/status', responseformat='xml' )
    orders = rlt.xpath( '//order' )
    for o in orders:
      if o.attrib['status'] == 'PLACED': continue
      return o.attrib['id']
    return False

  def get_order( self, orderid ):
    rlt = self.do_request( '/webservices/user/'+str( self.userid )+'/orders/order/' + str( orderid ) )
    return rlt

  def get_last_order_details( self ):
    orderid = self.get_last_orderid()
    return self.get_order( orderid )

def main():
  parser = argparse.ArgumentParser(description="Get your last Ocado shopping list in todo.txt format")
  parser.add_argument("-u", "--username", help="Ocado username")
  parser.add_argument("-p", "--password", help="Ocado password")
  args = parser.parse_args()
  if len( sys.argv)==1:
    parser.print_help()
    return
  oc = OcadoClient(args.username,args.password)
  order = oc.get_last_order_details()
  if order:
    for item in order['items']:
      q = item['quantity']
      if 'delivered' not in q.keys(): q['delivered'] = 'x'
      print re.sub( r'[^\x00-\x7F]+','?',item['desc'] ) + ' (' + q['delivered'] + '/' +q['ordered']+ ')' + ' @ocado +' + item['category']

if __name__ == "__main__":
  main()

