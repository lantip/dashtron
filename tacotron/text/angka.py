import re

_comma_number_re = re.compile(r'([0-9][0-9\.]+[0-9])')
_decimal_number_re = re.compile(r'([0-9]+\,[0-9]+)')
_pounds_re = re.compile(r'£([0-9\,]*[0-9]+)')
_rupiah_re = re.compile(r'rp([0-9\.\,]*[0-9]+)')
_number_re = re.compile(r'[0-9]+')


def _hilangkan_titik(m):
    return m.group(1).replace('.', '')


def _expand_desimal(m):
    return m.group(1).replace(',', ' koma ')


def _expand_rupiah(m):
    match = m.group(1)
    parts = match.split(',')
    if len(parts) > 2:
        return match + ' rupiah'  # Unexpected format
    rupiah = int(parts[0]) if parts[0] else 0
    sen = int(parts[1]) if len(parts) > 1 and parts[1] else 0
    if rupiah and sen:
        rupiah_unit = 'rupiah'
        sen_unit = 'sen'
        return '%s %s, %s %s' % (rupiah, rupiah_unit, sen, sen_unit)
    elif rupiah:
        rupiah_unit = 'rupiah'
        return '%s %s' % (rupiah, rupiah_unit)
    elif sen:
        sen_unit = 'sen'
        return '%s %s' % (sen, sen_unit)
    else:
        return 'nol rupiah'

def terbilang(bil):
    angka = ["","satu","dua","tiga","empat","lima","enam",
             "tujuh","delapan","sembilan","sepuluh","sebelas"]
    hasil = " "
    n = int(bil)
    if n>= 0 and n <= 11:
        hasil = angka[n]
    elif n <20:
        hasil = terbilang (n-10) + " belas "
    elif n <100:
        hasil = terbilang (n/10) + " puluh " + terbilang (n%10)
    elif n <200:
        hasil = " seratus " + terbilang (n-100)
    elif n <1000:
        hasil = terbilang (n/100) + " ratus " + terbilang (n%100)
    elif n <2000:
        hasil = " seribu " + terbilang (n-1000)
    elif n <1000000:
        hasil = terbilang (n/1000) + " ribu " + terbilang (n%1000)
    elif n <1000000000:
        hasil = terbilang (n/1000000) + " juta " + terbilang (n%1000000)
    elif n <1000000000000:
        hasil = terbilang (n/1000000000) + " milyar " + terbilang (n%1000000000)
    elif n <1000000000000000:
        hasil = terbilang (n/1000000000000) + " triliyun " + terbilang (n%1000000000000)
    elif n == 1000000000000000:
        hasil = "satu kuadriliun"
    else:
        hasil = bil
    return hasil


def _expand_number(m):    
    num = int(m.group(0))
    return terbilang(num)


def normalize_angka(text):
    text = re.sub(_comma_number_re, _hilangkan_titik, text)
    text = re.sub(_pounds_re, r'\1 pounds', text)
    text = re.sub(_rupiah_re, _expand_rupiah, text)
    text = re.sub(_decimal_number_re, _expand_desimal, text)
    text = re.sub(_number_re, _expand_number, text)
    return text
