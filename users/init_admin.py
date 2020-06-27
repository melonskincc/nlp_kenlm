from users.models import Users
from utils.libs import random_base32, gen_qrcode

try:
    admin = Users.objects.get(username='admin')
except Users.DoesNotExist:
    sk = random_base32()
    qrcode_url = gen_qrcode('admin', sk)
    admin = Users.objects.create_superuser(username='admin', password='admin123456', email='1111@163.com',
                                           qrcode_url=qrcode_url, secret_key=sk)
# Users.objects.get(username='admin').delete()
