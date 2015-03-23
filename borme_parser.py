#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import sys
import time
import unicodedata


def remove_accents(str):
    return ''.join((c for c in unicodedata.normalize('NFKD', unicode(str, 'utf-8')) if unicodedata.category(c) != 'Mn'))


# Palabras clave con argumentos
ARG_KEYWORDS = ['Nombramientos', 'Revocaciones', 'Ceses/Dimisiones', 'Modificaciones estatutarias', 'Cambio de objeto social',
                'Cambio de denominación social', 'Cambio de domicilio social', 'Ampliacion del objeto social',
                'Sociedad unipersonal', 'Disolución', 'Reelecciones', 'Constitución',
                'Articulo 378.5 del Reglamento del Registro Mercantil', 'Otros conceptos',
                'Ampliación de capital', 'Reducción de capital', 'Situación concursal', 'Fusión por absorción',
                'Suspensión de pagos', 'Transformación de sociedad', 'Cancelaciones de oficio de nombramientos']

# Palabras clave sin argumentos
NOARG_KEYWORDS = ['Sociedad unipersonal', 'Extinción', 'Declaración de unipersonalidad',
                  'Pérdida del caracter de unipersonalidad', 'Reapertura hoja registral',
                  'Adaptación Ley 2/95',
                  'Cierre provisional hoja registral por baja en el índice de Entidades Jurídicas']

# Palabras clave seguidas por :
COLON_KEYWORDS = ['Cambio de identidad del socio único', 'Fe de erratas', 'Socio único']

# Palabra clave
ENDING_KEYWORD = ['Datos registrales']

ALL_KEYWORDS = ARG_KEYWORDS + NOARG_KEYWORDS + COLON_KEYWORDS + ENDING_KEYWORD

DICT_KEYWORDS = {kw: remove_accents(kw).replace(' del ', ' ').replace(' por ', ' ').replace(' de ', ' ')\
                .replace(' ', '_').replace('/', '_').replace('.', '_').lower() for kw in ALL_KEYWORDS}
"""
>>> DICT_KEYWORDS.values()
[u'revocaciones', u'cambio_objeto_social', u'reelecciones', u'otros_conceptos', u'fe_erratas', u'sociedad_unipersonal', u'declaracion_unipersonalidad', u'constitucion', u'suspension_pagos', u'
perdida_caracter_unipersonalidad', u'cancelaciones_oficio_nombramientos', u'datos_registrales', u'cambio_domicilio_social', u'disolucion', u'ampliacion_objeto_social', u'cierre_provisional_hoj
a_registral_baja_en_el_indice_entidades_juridicas', u'ceses_dimisiones', u'nombramientos', u'situacion_concursal', u'modificaciones_estatutarias', u'ampliacion_capital', u'adaptacion_ley_2_95'
, u'cambio_denominacion_social', u'extincion', u'reduccion_capital', u'cambio_identidad_socio_unico', u'transformacion_sociedad', u'reapertura_hoja_registral', u'socio_unico', u'articulo_378_5
_reglamento_registro_mercantil', u'fusion_absorcion']
"""

CARGOS_KEYWORD = ['Consejero', 'Presidente', 'Vicepresid', 'Secretario', 'Cons.Del.Man', 'Adm. Unico']

CSV_HEADERS = ['ID', 'Nombre']
CSV_HEADERS.extend(NOARG_KEYWORDS)
CSV_HEADERS.extend(COLON_KEYWORDS)
CSV_HEADERS.extend(ARG_KEYWORDS)
CSV_HEADERS.extend(ENDING_KEYWORD)


# Simplemente implementa parse_line
class LBCommonParser():
    LOGFILE = 'foo.log'
    DEFAULT_OUT_DIR = 'tmp'
    REWRITE = False  # Allows resuming
    NAME = '2'

    def __init__(self, _level=logging.INFO, output_csv=False):
        # Logs warnings, errors and criticals to stdout and file
        logging.basicConfig(filename=self.LOGFILE, level=_level, format='%(name)s: %(asctime)s %(message)s', datefmt='%Y-%m-%d %I:%M')
        self.logger = logging.getLogger("csvBORME")  # name

        h1 = logging.StreamHandler(sys.stdout)
        h1.setLevel(_level)
        self.logger.addHandler(h1)

        self.results = {'error': 0, 'skip': 0, 'ok': 0, 'warning': 0}
        self.csvline = {}
        self.CSV = output_csv

    def parse_line(self, filenameIn, filenameOut):
        raise NotImplementedError

    def parse_file(self, filenameIn, filenameOut):
        """
            Parse file according to BORME PDF format

            filename:
            filenameOut:
        """

        had_warning = False

        if os.path.isdir(filenameOut):
            filenameOut = os.path.join(filenameOut, os.path.basename(filenameIn))

        if os.path.exists(filenameOut) and not self.REWRITE:
            self.logger.info('Skipping file %s already exists and rewriting is disabled!' % filenameOut)
            return False

        # regexp
        fp = open(filenameIn, 'r')
        text = fp.read()
        fp.close()

        outfp = open(filenameOut, 'w')
        self.print_header(outfp)
        # TODO: Compilar las regexp para mayor eficiencia
        # http://stackoverflow.com/questions/16720541/python-string-replace-regular-expression
        # regexp = re.compile(...)
        # m = regexp.findal(...)

        for trozo in text.split('.\n\n'):
            self.csvline = {}
            trozo += '.'

            try:
                self.parse_line(trozo)

                self.logger.debug('###########')
                self.print_line(outfp)
                self.logger.debug('###########')
            except:
                had_warning = True
                self.logger.warning('###########')
                self.logger.warning('SKIPPING. Invalid data found:')
                self.logger.warning(trozo)
                self.logger.warning('###########')
                self.results['warning'] += 1

        outfp.close()

        if had_warning:
            self.results['error'] += 1

        return True

    def parse_dir(self, dirIn, dirOut):
        """
            Parse files in batch mode

            dirIn:
            dirOut:
        """
        gen = os.walk(dirIn)
        _, _, files = gen.next()
        total = len(files)

        for i, f in enumerate(files):
            filename = os.path.join(dirIn, f)
            if self.CSV:
                filenameOut = "%s.%s.csv" % (f, self.NAME)
            else:
                filenameOut = "%s.%s.plain" % (f, self.NAME)
            filenameOut = os.path.join(dirOut, filenameOut)

            self.logger.info("[%d/%d] Writing %s", i + 1, total, filenameOut)
            filename = os.path.join(dirIn, f)
            try:
                res = self.parse_file(filename, filenameOut)
                if res:
                    self.logger.info("OK")
                    self.results['ok'] += 1
                else:
                    self.logger.info("SKIP")
                    self.results['skip'] += 1
            except:
                self.logger.info("ERROR")
                self.logger.exception("Error processing file %s", filename)
                self.results['error'] += 1

    def save_field(self, content):
        self.logger.debug('Guardando %s', content)

        self.csvline[content[0]] = content[1]

        if not 'total' in self.csvline:
            self.csvline['total'] = 1
        else:
            self.csvline['total'] += 1

    def print_header(self, outfp):
        line = ""
        if self.CSV:
            for k in CSV_HEADERS:
                line += '"' + k + '",'
            line = line[:-1] + '\n'
        else:
            for k in CSV_HEADERS:
                line += k + '\n'
            line += '----------------------------------------------------------\n'
        self.logger.debug(line)
        outfp.write(line)

    def print_line(self, outfp):
        self.logger.debug('Keys: %s total: %d', self.csvline.keys(), self.csvline['total'])
        self.logger.debug('%s', self.csvline)
        line = ""

        if self.CSV:
            # print CSV-friendly
            for k in CSV_HEADERS:
                if k in self.csvline:
                    content = '"' + self.csvline[k].replace('"', '\\"') + '"'
                    line += content
                line += ','
            line = line[:-1] + '\n'
        else:
            for k in CSV_HEADERS:
                if k in self.csvline:
                    line += self.csvline[k]
                line += '\n'
            line += '----------------------------------------------------------\n'
        self.logger.debug(line)
        outfp.write(line)

    def show_stats(self):
        elapsed_time = time.time() - self.start_time
        self.logger.info('\nElapsed time: %.2f seconds' % elapsed_time)
        self.logger.info('Results:')
        self.logger.info('  Parsed: %d' % self.results['ok'])
        self.logger.info('  Warning: %d' % self.results['warning'])
        self.logger.info('  Skipped: %d' % self.results['skip'])

        if self.results['error'] > 0:
            self.logger.info('  Errors: %d (see %s for more information).' % (self.results['error'], self.LOGFILE))
        else:
            self.logger.info('  Errors: %d' % self.results['error'])

    def main(self, argv):
        self.start_time = time.time()

        filenameIn = argv[1]
        if os.path.isdir(filenameIn):
            filenameOut = argv[2] if len(argv) > 2 else self.DEFAULT_OUT_DIR
            if os.path.isdir(filenameOut):
                self.parse_dir(filenameIn, filenameOut)
            else:
                if filenameOut == self.DEFAULT_OUT_DIR:
                    os.mkdir(self.DEFAULT_OUT_DIR)
                    self.parse_dir(filenameIn, filenameOut)
                else:
                    self.logger.exception("If first parameter is a directory, second one must be too and exist")
                    sys.exit(1)

        elif os.path.isfile(filenameIn):
            if self.CSV:
                filenameOut = argv[2] if len(argv) > 2 else '%s.%s.csv' % (os.path.basename(filenameIn), self.NAME)
            else:
                filenameOut = argv[2] if len(argv) > 2 else '%s.%s.plain' % (os.path.basename(filenameIn), self.NAME)
            filenameOut = os.path.join(self.DEFAULT_OUT_DIR, filenameOut)
            self.logger.info('[1/1] Writing %s' % filenameOut)
            try:
                res = self.parse_file(filenameIn, filenameOut)
                if res:
                    self.logger.info('OK')
                    self.results['ok'] += 1
                else:
                    self.logger.info('SKIP')
                    self.results['skip'] += 1
            except:
                self.logger.info('ERROR')
                self.logger.exception("Error processing file %s", filenameIn)
                self.results['error'] += 1
        else:
            self.logger.error("File %s doesn't exist" % filenameIn)
