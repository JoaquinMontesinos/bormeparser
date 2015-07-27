#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .acto import ACTO
#from .download import get_url_pdf, download_pdf
from .exceptions import BormeAlreadyDownloadedException, BormeInvalidActoException, BormeAnuncioNotFound
#from .parser import parse as parse_borme
#from .seccion import SECCION
#from .provincia import PROVINCIA
import datetime

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARN)


class BormeAnuncio(object):
    """
    Representa un anuncio con un conjunto de actos mercantiles (Constitucion, Nombramientos, ...)
    """

    def __init__(self, id, empresa, actos):
        logger.debug('new BormeAnuncio(%s) %s' % (id, empresa))
        self.id = id
        self.empresa = empresa
        self.datos_registrales = ""
        self._set_actos(actos)

    def _set_actos(self, actos):
        for acto_name in actos.keys():
            if acto_name == 'Datos registrales':
                self.datos_registrales = actos[acto_name]
                continue
            if acto_name not in ACTO.ALL_KEYWORDS:
                logger.warning('Invalid acto found: %s' % acto_name)
                #raise BormeInvalidActoException('Invalid acto found: %s' % acto_name)

        try:
            del actos['Datos registrales']
        except KeyError:
            pass
        self.actos = actos

    def get_datos_registrales(self):
        return self.datos_registrales

    def get_actos(self):
        return self.actos

    def __repr__(self):
        return "<BormeAnuncio(%d) %s (%d)>" % (self.id, self.empresa, len(self.actos))


class BormeXML(object):
    pass


# TODO: Iterador de anuncios
# TODO: Info
# TODO: Create instance directly from filename
class Borme(object):

    def __init__(self, date, seccion, provincia, num, cve, anuncios=None, url=None, filename=None):
        if isinstance(date, tuple):
            date = datetime.date(year=date[0], month=date[1], day=date[2])
        self.date = date
        self.seccion = seccion
        self.provincia = provincia
        self.num = num
        self.cve = cve
        self.url = url
        self.filename = filename
        self._parsed = False
        self.info = {}
        self._set_anuncios(anuncios)

    @classmethod
    def from_file(cls, filename):
        raise NotImplementedError

    def _set_anuncios(self, anuncios):
        self.anuncios = {}
        for anuncio in anuncios:
            self.anuncios[anuncio.id] = anuncio

    def get_url(self):
        if self.url is None:
            self.url = get_url_pdf(self.date, self.seccion, self.provincia)
        return self.url

    def get_info(self):
        #borme['info'] = {'pages': 5, 'anuncios': 38, 'fromanuncio': 12222, 'toanuncio': 12260}
        #return self.info
        raise NotImplementedError

    def get_anuncio(self, anuncio_id):
        try:
            return self.anuncios[anuncio_id]
        except KeyError:
            raise BormeAnuncioNotFound('Anuncio %d not found in BORME %s' % (anuncio_id, str(self)))

    def get_anuncios_ids(self):
        """
        [BormeAnuncio]
        """
        return list(self.anuncios.values())

    def get_anuncios(self):
        """
        [BormeAnuncio]
        """
        return list(self.anuncios.values())

    def download(self, filename):
        if self.filename is not None:
            raise BormeAlreadyDownloadedException(filename)
        downloaded = download_pdf(self.date, filename, self.seccion, self.provincia)
        if downloaded:
            self.filename = filename
        return downloaded

    def __repr__(self):
        return "<Borme(%s) seccion:%s provincia:%s>" % (self.date, self.seccion, self.provincia)
