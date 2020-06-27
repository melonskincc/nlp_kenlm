import random as _random
from urllib.parse import urlencode
import os, time, datetime, hmac, hashlib, base64, qrcode, re
from NLP.settings import STATICFILES_DIRS, STATIC_URL
from aip import AipNlp

APP_ID = ''
API_KEY = ''
SECRET_KEY = ''


def byte_secret(secret: str):
    missing_padding = len(secret) % 8
    if missing_padding != 0:
        secret += '=' * (8 - missing_padding)
    return base64.b32decode(secret, casefold=True)


def int_to_bytestring(i: int, padding=8):
    result = bytearray()
    while i != 0:
        result.append(i & 0xFF)
        i >>= 8
    return bytes(bytearray(reversed(result)).rjust(padding, b'\0'))


def generate_otp(secret: str):
    for_time = datetime.datetime.now()
    i = time.mktime(for_time.timetuple())
    input = int(i / 30)
    digest = hashlib.sha1
    digits = 6
    if input < 0:
        raise ValueError('input must be positive integer')
    hasher = hmac.new(byte_secret(secret), int_to_bytestring(input), digest)
    hmac_hash = bytearray(hasher.digest())
    offset = hmac_hash[-1] & 0xf
    code = ((hmac_hash[offset] & 0x7f) << 24 |
            (hmac_hash[offset + 1] & 0xff) << 16 |
            (hmac_hash[offset + 2] & 0xff) << 8 |
            (hmac_hash[offset + 3] & 0xff))
    str_code = str(code % 10 ** digits)
    while len(str_code) < digits:
        str_code = '0' + str_code
    return str_code


def random_base32(length=16, random=_random.SystemRandom(),
                  chars=list('ABCDEFGHIJKLMNOPQRSTUVWXYZ234567')):
    # 一个账号只需要生成一次密钥
    return ''.join(
        random.choice(chars)
        for _ in range(length)
    )


def gen_qrcode(username, secret):
    # 用户生成二维码
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    data = "otpauth://totp/{}?".format(username)
    query_data = {'secret': secret, 'issuer': '中文智能纠错平台'}
    data += urlencode(query_data)
    qr.add_data(data)
    qr.make()
    if not os.path.exists(STATICFILES_DIRS[0] + '/google_auth_qrcode/'):
        os.mkdir(STATICFILES_DIRS[0] + '/google_auth_qrcode/')
    img = qr.make_image(fill_color="black", back_color="white")
    qrcode_url = STATIC_URL + 'google_auth_qrcode/{}_qrcode.png'.format(username)
    img.save(STATICFILES_DIRS[0] + '/google_auth_qrcode/{}_qrcode.png'.format(username))
    return qrcode_url


def file_iterator(path, chunck_size=512):
    with open(path, 'rb') as f:
        while True:
            c = f.read(chunck_size)
            if c:
                yield c
            else:
                break


def baidu_correct(text: str) -> str:
    """百度纠错api"""
    client = AipNlp(APP_ID, API_KEY, SECRET_KEY)
    client.setConnectionTimeoutInMillis(10000)
    client.setSocketTimeoutInMillis(10000)
    try:
        s = client.ecnet(text)
    except Exception as e:
        print(repr(e))
        return text
    else:
        import time,logging
        time.sleep(0.1)
        logging.info(s)
        if 'error_code' in s.keys():
            print(s)
            return text
        return s.get('item').get('vec_fragment')


zh_pattern = re.compile(u'[\u4e00-\u9fa5]+')


def contain_zh(word):
    '''
    判断传入字符串是否包含中文
    :param word: 待判断字符串
    :return: True:包含中文  False:不包含中文
    '''
    global zh_pattern
    match = zh_pattern.search(word)

    return match


if __name__ == '__main__':
    gen_qrcode('admin', '12312edawdaw')
    print(baidu_correct('少先队因该给老人让坐'))
