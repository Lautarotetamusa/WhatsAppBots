import spintax
import re

def validate(msg):
    spin = spintax.spin(msg)
    print(spin)
    return not('{' in spin or '}' in spin or '|' in spin)

def get_fields(msg):
    #Match all the fields names
    #ej: fields([title]kdlsmieid["nombre"]dskaodw["edad"]]) => ["title", "nombre", "edad"]
    pat = r'(?<=\[).+?(?=\])'
    return re.findall(pat, msg)

def spin(msg):
    return spintax.spin(msg)

def format(msg, post):
    spin = spintax.spin(msg)

    format = spin.replace("[","{").replace("]","}")

    #Esto lo hacemos por si acaso ese campo no existe en algun post
    fields = get_fields(spin)
    for field in fields:
        if field not in post:
            post[field] = ""

    return format.format(**post)
