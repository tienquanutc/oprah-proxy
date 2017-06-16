#!/usr/bin/env python3

import base64
import hashlib
import uuid
import logging
import os
import sys

try:
    import requests
except ImportError:
    logging.error('Cannot import requests')
    logging.debug('Please install Requests for Python 3, see '
                  'http://docs.python-requests.org/en/master/user/install/ or use your '
                  'favorite package manager (e.g. apt-get install python3-requests)')
    exit(2)


class OprahProxy:
    """ Everybody gets a proxy! """

    client_type = ''
    client_key = ''
    session = None
    device_id = ''
    device_id_hash = ''
    device_password = ''

    def __init__(self, client_type, client_key):
        self.client_type = client_type
        self.client_key = client_key
        self.session = requests.Session()

    def post(self, url, data):
        headers = {'SE-Client-Type': self.client_type,
                   'SE-Client-API-Key': self.client_key,
                   'SE-Operating-System': 'Windows'}

        result = self.session.post('https://api.surfeasy.com%s' % url, data,
                                   headers=headers).json()
        code = list(result['return_code'].keys())[0]
        if code != '0':
            logging.debug('ERROR: %s' % result['return_code'][code])
            exit(1)
        return result

    def register_subscriber(self):
        logging.debug('Call register_subscriber')
        email = '%s@%s.surfeasy.vpn' % (uuid.uuid4(), self.client_type)
        password = uuid.uuid4()
        password_hash = hashlib.sha1(
            str(password).encode('ascii')).hexdigest().upper()
        logging.debug('Your SurfEasy email: %s' % email)
        logging.debug('Your SurfEasy password: %s' % password)
        logging.debug('Your SurfEasy password hash: %s' % password_hash)
        logging.debug("These are not the credentials you are looking for "
                      "(you won't probably need these, ever)")

        data = {'email': email,
                'password': password_hash}
        result = self.post('/v2/register_subscriber', data)
        logging.debug('Subscriber registered')
        return result

    def register_device(self):
        logging.debug('Call register_device')
        data = {'client_type': self.client_type,
                'device_hash': '4BE7D6F1BD040DE45A371FD831167BC108554111',
                'device_name': 'Opera-Browser-Client'}

        result = self.post('/v2/register_device', data)
        self.device_id = result['data']['device_id']
        logging.debug('Device id: %s' % self.device_id)
        self.device_id_hash = hashlib.sha1(
            str(self.device_id).encode('ascii')).hexdigest().upper()
        self.device_password = result['data']['device_password']
        logging.debug('Device registered')

    def geo_list(self):
        logging.debug('Call geo_list')
        data = {'device_id': self.device_id_hash}
        result = self.post('/v2/geo_list', data)
        codes = []
        for geo in result['data']['geos']:
            codes.append(geo['country_code'])
            logging.info('Supported country: %s %s' %
                         (geo['country_code'], geo['country']))
        logging.debug('Geo list fetched')
        return codes

    def discover(self, country_code):
        proxies = [{
            'hostname': '%s.opera-proxy.net' % country_code.lower(),
            'port': 443
        }]
        logging.info('Proxy in %s %s:%s' % (country_code, proxies[0]['hostname'], proxies[0]['port']))
        return proxies

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)-8s %(message)s'
    )

    logging.debug('++++++++++++++++++++++++++=======================~~~~~~~::::')
    logging.debug(',..,,,.,,...,,,.,,,,,,,,,,............,.....,.,,::::~~======')
    logging.debug(',,,,,:,,,,,,,,,,,,,,                    ,.,,,,,,,,,,,,,....~')
    logging.debug('~~~~~~~:::::::::::::  YOU GET A PROXY!  ,,,,,,,,,,,,,,,,,:~=')
    logging.debug('~~===~~~~::::::::::.                    ,,,,,,,,,,,,,,,~~~:~')
    logging.debug('::~:::::::::::::::,,...,~=::~=~:.....,,,,,,,,,,,,,,,:~:~:,::')
    logging.debug('??+=..,++++++++++=.....:===I+~=~....,,~~=~~~~~~~:~====~,,::~')
    logging.debug('::~....,...............~=~~~~:=~,...,.~~~======~==++=~:====+')
    logging.debug('::~...,:,,,,,,,,.......:==~+=:~:,.....,,,,,,,~~~====~,,,,,,,')
    logging.debug(':::~~~:,::,,::::,......+~~===~:,.....,,,,,,~~~~~==~,,,,....,')
    logging.debug('~:~:,,,,,:::::,..........~~::~,:....:~~~~~::::~:::::,,,,,,,,')
    logging.debug('~...~~~,,::~~::~:........~~~:~::.:,,:~::::::::::::::::::::::')
    logging.debug('+..???+?~,::::::::::::~:~::~~~:~::::::::::::::::~~=~~~~~~~~=')
    logging.debug('...?????+?,.:::::::::::~~:~~::~:::::::::::::::,~++++++++++++')
    logging.debug('?=??????+??~,::::::::~~~~~~~~~~::::::::::::::,=+++++++++++++')
    logging.debug('????????????::::::,::~~~~~~~~~~:::::::::::::,+++++++++++++++')
    logging.debug('??+??????????:,,::,:::~~~~~~~:::::::::::::,+++++++++++++++++')
    logging.debug('??????????????+,,,,:::~~,~~~~~:::=,:::::,?+?++++++++++++++++')
    logging.debug('????????????????+,:::~~:,~~~~~~~~:~::::=+??+?++?++++++++++++')
    logging.debug('??????????????????:::~~~~~~~~~~~:::::::???????++++++++++++++')
    logging.debug('??????????????????=:::~~~~~~~~~::::::::+??????+++++?+?++++++')
    logging.debug('=+==+====++++++++==:::~:,~~~~~:::,::::~====~~::::,,...,:~~=+')
    logging.debug('++++++++++++===++++::~:~~~~~~::::~::::=+++++++++++++========')
    logging.debug('=====+++++=====++++:~:~~~~~~::::::::::~++===================')
    logging.debug('+++==+======+++                           ==================')
    logging.debug('~~~~==========~  EVERYBODY GETS A PROXY!  ~~~~~~~~~~~~~~~~~~')
    logging.debug('~~~~~~~~~~~===~                           ~~~~~~~~~~~~~~~~~~')
    logging.debug('=============++===:::::::::::::::::::::~~~~~~~~~~~~~~~~~~~:~')
    logging.debug('https://github.com/spaze/oprah-proxy :::==~=~~~~~~~~=~~~~~~~')

    if len(sys.argv) < 2:
        logging.error('Missing client_type')
    if len(sys.argv) < 3:
        logging.error('Missing client_key')
        logging.error('Usage: %s <client_type> <client_key>' % os.path.basename(sys.argv[0]));
        exit(1)

    op = OprahProxy(sys.argv[1], sys.argv[2])
    op.register_subscriber()
    op.register_device()
    example_proxy = None
    for country_code in op.geo_list():
        for item in op.discover(country_code):
            if not example_proxy and item['port'] == 443:
                example_proxy = '%s:%s' % (item['hostname'], item['port'])

    logging.info('Pick a proxy from the list above and use these credentials:')
    logging.info('Username: %s' % op.device_id_hash)
    logging.info('Password: %s' % op.device_password)
    creds = ('%s:%s' % (op.device_id_hash, op.device_password)).encode('ascii')
    header = 'Proxy-Authorization: Basic %s' % base64.b64encode(creds).decode('ascii')
    logging.info('HTTP header %s' % header)
    logging.debug('Example bash command: URL="http://www.opera.com" PROXY=%s '
                  'HEADER="%s"; echo -e "GET $URL HTTP/1.0\\n$HEADER\\n\\n" | '
                  'openssl s_client -connect $PROXY -ign_eof' %
                  (example_proxy, header))
    logging.debug('For PAC-file for other browsers see '
                  'https://github.com/spaze/oprah-proxy#usage-with-other-browsers')
