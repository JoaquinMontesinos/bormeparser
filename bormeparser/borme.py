#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .acto import ACTO
#from .download import get_url_pdf, download_pdf
from .exceptions import BormeAlreadyDownloadedException, BormeInvalidActoException
#from .parser import parse as parse_borme
import datetime

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARN)

class BormeActo(object):
    """
    Representa un conjunto de actos mercantiles (Constitucion, Nombramientos, ...)
    """

    def __init__(self, id, empresa, actos):
        logger.debug('new BormeActo(%s) %s' % (id, empresa))
        self.id = id
        self.empresa = empresa
        self._set_actos(actos)

    def _set_actos(self, actos):
        for acto in actos.keys():
            if acto not in ACTO.ALL_KEYWORDS:
                logger.warning('Invalid acto found: %s\n' % acto)
                #raise BormeInvalidActoException('Invalid acto found: %s' % acto)
        self.actos = actos

    def get_actos(self):
        return self.actos

    def __repr__(self):
        return "<BormeActo(%d) %s (%d)>" % (self.id, self.empresa, len(self.actos)-1)


class BormeXML(object):
    pass

# TODO: Iterador de actos
# TODO: Info
# TODO: Create instance directly from filename
class Borme(object):

    def __init__(self, date, seccion, provincia, num, actos=None, url=None, filename=None):
        if isinstance(date, tuple):
            date = datetime.date(year=date[0], month=date[1], day=date[2])
        self.date = date
        self.seccion = seccion
        self.provincia = provincia
        self.num = num
        self.url = url
        self.filename = filename
        self._parsed = False
        self.info = {}
        self._set_actos(actos)

    def _set_actos(self, actos):
        self.actos = {}
        for acto in actos:
            self.actos[acto.id] = acto

    def get_url(self):
        if self.url is None:
            self.url = get_url_pdf(self.date, self.seccion, self.provincia)
        return self.url

    def get_info(self):
        #borme['info'] = {'pages': 5, 'actos': 38, 'fromacto': 12222, 'toacto': 12260}
        #return self.info
        raise NotImplementedError

    def get_acto(self, acto_id):
        return self.actos[acto_id]

    def get_actos(self):
        """
        [BormeActo]
        """
        return list(self.actos.values())

    def download(self, filename):
        if self.filename is not None:
            raise BormeAlreadyDownloadedException(filename)
        downloaded = download_pdf(self.date, filename, self.seccion, self.provincia)
        if downloaded:
            self.filename = filename
        return downloaded

    @staticmethod
    def from_file(filename):
        #data = parse_borme(filename)
        # extraer date, seccion y provincia
        #return Borme()
        raise NotImplementedError

    def __repr__(self):
        return "<Borme(%s) seccion:%s provincia:%s>" % (self.date, self.seccion, self.provincia)
