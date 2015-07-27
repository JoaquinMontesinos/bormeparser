#!/usr/bin/env python
import bormeparser
import bormeparser.borme
import logging
import sys


if __name__ == '__main__':

    # set logger DEBUG
    if len(sys.argv) == 3 and sys.argv[2] == '--debug':
        bormeparser.borme.logger.setLevel(logging.DEBUG)

    borme = bormeparser.parse(sys.argv[1])

    for anuncio in borme.get_anuncios():
        print('Anuncio %d' % anuncio.id)
        print('-' * (8 + len(str(anuncio.id))))
        print()
        for acto, valor in anuncio.get_actos():
            print('  %s' % acto)
            print('    %s' % valor)
        print()

    print('Otros')
    print('-----')
    print()
    print('  CVE: %s' % borme.cve)
    print('  Fecha: %s' % borme.date)
    print('  Num: %s' % borme.num)
    print('  Provincia: %s' % borme.provincia)
    print('  Seccion: %s' % borme.seccion)
    print('  Anuncios incluidos: %d' % len(borme.get_anuncios()))
