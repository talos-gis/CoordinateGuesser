from .normalize import extractSignfromGeo
import re

"""
the first can return value 
-1 to signify that the value cannot be handled by unmanglers
0 and 1 to signify that the value can only be handled as an x or y coordinate, respectivly
2 to signify that it can be both 
"""

def tofloatindif(x):
    """converts european-style floating point numbers and sane-style floating point numbers to floats"""
    x = x.replace(',', '.')
    return float(x.replace('.', '', x.count('.') - 1))

#todo abc

class concattedDMS:
    """903030->91.00833"""
    @staticmethod
    def split(x):
        blacklist = [chr(u) for u in [0x00B0, 0x2032, 0x2033]] #° , ', "
        for b in blacklist:
            x = x.replace(b, '', 3)
        sign = 1
        if x.startswith('-'):
            sign = -1
            x = x[1:]
        if len(x) > 7 or len(x) < 4:
            raise ValueError('bad input length')
        lend = len(x)-4
        dd = 0 if lend == 0 else int(x[:lend])
        mm = int(x[lend:lend+2])
        ss = int(x[lend+2:])
        return sign*dd, sign*mm, sign*ss

    def can(self, x):
        x, sign, pos = extractSignfromGeo(x)
        try:
            d, m, s = self.split(x)
        except ValueError:
            return -1, None
        if d > 360 or d < -180:
            return -1, None
        if m >= 60:
            return -1, None
        if s >= 60:
            return -1, None
        if d > 90 or d < -90:
            pos = 0
        return pos, (d,m,s,sign)

    def toHalfCor(self, x, canval):
        d, m, s, sign = canval
        return (d+(m+s/60.0)/60.0) * sign

    def __str__(self):
        return "ddmmss"

class identDMS:
    """90 30 30->91.00833"""
    @staticmethod
    def split(x):
        blacklist = [chr(u) for u in [0x0064, 0x006d, 0x0022]]
        for b in blacklist:
            x = x.replace(b, ' ', 1)
        split = [i for i in re.split('[^\d.,]+',x,3) if len(i) > 0]
        return split

    def can(self,x):
        x,sign,pos = extractSignfromGeo(x)
        try:
            split = self.split(x)
        except ValueError:
            return -1, None
        if len(split) < 3:
            split += ["0"] * (3 - len(split))
        if len(split) != 3:
            return -1, None
        try:
            d, m, s = map(lambda s: tofloatindif(s), split)
        except ValueError:
            return -1, None
        return pos, (d,m,s,sign)

    def toHalfCor(self, x, canval):
        d,m,s, sign = canval
        return (d+(m+s/60.0)/60.0) * sign

    def __str__(self):
        return "d m s"

class identDecDegGeo:
    """91.00833 -> 91.00833"""
    def can(self, x):
        x, sign, pos = extractSignfromGeo(x)
        try:
            d = tofloatindif(x)
        except ValueError:
            return -1, None
        d *= sign
        if d > 360 or d < -180:
            return -1, None
        if d > 90 or d < -90:
            pos = 0
        return pos, d

    def toHalfCor(self, x, canval):
        return canval

    def __str__(self):
        return "geodecdeg"

class identDecMinGeo:
    """
    5460.4998 -> 91.00833
    raw minutes
    """
    def can(self, x):
        x, sign, pos = extractSignfromGeo(x)
        try:
            d = tofloatindif(x)
        except ValueError:
            return -1, None
        d /= 60.0
        d *= sign
        if d > 360 or d < -180:
            return -1, None
        if d > 90 or d < -90:
            pos = 0
        return pos, d

    def toHalfCor(self, x, canval):
        return canval

    def __str__(self):
        return "geodecmin"

class identDecSecGeo:
    """
    327629.98799999995 -> 91.00833
    raw seconds
    """
    def can(self, x):
        x, sign, pos = extractSignfromGeo(x)
        try:
            d = tofloatindif(x)
        except ValueError:
            return -1, None
        d /= (60.0*60.0)
        d *= sign
        if d > 360 or d < -180:
            return -1, None
        if d > 90 or d < -90:
            pos = 0
        return pos, d
    def toHalfCor(self, x, canval):
        return canval
    def __str__(self):
        return "geodecsec"

class identUTM:
    """raw utm"""
    def can(self, x):

        (abx, sign, pos) = extractSignfromGeo(x)  # TODO needs to handle WNSE! - seems like already done
        try:
            d = sign*tofloatindif(abx)
        except ValueError:
            return -1, None
        return pos, d

    def toHalfCor(self, x, canval):
        return canval

    def __str__(self):
        return "utmcoor"
