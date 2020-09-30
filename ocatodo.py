#!/usr/bin/python
from lxml import etree
import argparse, requests, sys, re, datetime

class OcadoClient:

  userid    = None
  sessionid = '8BFF9C71-CA91-4BA5-BE99-605806AEE64F'
  deviceid  = '8d8c124b51fe43eb'
  authtoken = '861e3a4f4da0819608f4c928da0274f6'
  useragent = 'Ocado-Android-Application/1.84.0'
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
      print(response.text)
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
      if o.attrib['status'] == 'FUTURE': continue
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
  parser.add_argument("-c", "--context", help="List name / context", default="ocado")
  parser.add_argument("-e", "--expires-within", help="Show only items that will expire within this number of days from now", type=int)
  parser.add_argument("-t", "--today", action="store_true", help="Only output anything if the last order is being delivered today")
  parser.add_argument("-s", "--sku", action="store_true", help="Include item SKU")
  parser.add_argument("-x", "--expand", action="store_true", help="Expand out grouped items into one line per item")
  args = parser.parse_args()
  if len( sys.argv)==1:
    parser.print_help()
    return
  oc = OcadoClient(args.username,args.password)
  order = oc.get_last_order_details()
  
  # filter on expiry date
  expiresbefore = None
  if args.expires_within:
    expiresbefore = (datetime.datetime.now() + datetime.timedelta(days=args.expires_within)).strftime('%Y-%m-%d')

  if order:
    if args.today and datetime.datetime.now().strftime('%Y-%m-%d') != order['delivery']['slot']['start'][:10]:
      return
    for item in order['items']:
      if expiresbefore and ( 'expire' not in list(item.keys()) or item['expire']['expireDate'][:10] > expiresbefore):
        continue
      q = item['quantity']
      if 'delivered' not in list(q.keys()): q['delivered'] = 'x'
      if args.expand: repeat = int(q['delivered'])
      else: repeat = 1
      for i in range(1,repeat+1):
        print(order['delivery']['slot']['start'][:10] + ' ' + re.sub( r'[^\x00-\x7F]+','?',item['desc'] ) + ' (' + q['delivered'] + '/' +q['ordered']+ ')', end=' ')
        if args.expand: print('#' + str(i), end=' ')
        print('@'+args.context+' +' + item['category'], end=' ')
        if 'expire' in list(item.keys()):
          e = item['expire']
          print('due:' + e['expireDate'][:10], end=' ')
        if args.sku:
          print('['+item['sku']+']', end=' ')
        print('')


if __name__ == "__main__":
  main()

