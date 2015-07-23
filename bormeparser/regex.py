#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

from bormeparser.acto import ACTO
from bormeparser.cargo import CARGO

esc_arg_keywords = [x.replace('.', '\.') for x in ACTO.ALL_KEYWORDS]
esc_colon_keywords = [x.replace('.', '\.') for x in ACTO.COLON_KEYWORDS]
esc_noarg_keywords = [x.replace('.', '\.') for x in ACTO.NOARG_KEYWORDS]
esc_ending_keywords = [x.replace('.', '\.') for x in ACTO.ENDING_KEYWORDS]

# -- ACTOS --
# OR de las palabras clave con argumentos
RE_ARG_KEYWORDS = '(%s)' % '|'.join(esc_arg_keywords)
# OR de las palabras clave, "non grouping"
RE_ALL_KEYWORDS_NG = '(?:%s|%s|%s|%s)' % ('|'.join(esc_arg_keywords), '|'.join(esc_colon_keywords),
                                          '|'.join(esc_noarg_keywords), esc_ending_keywords[0])
# OR de las palabras clave sin argumentos
RE_NOARG_KEYWORDS = '(%s)' % '|'.join(esc_noarg_keywords)
# OR de las palabras clave con argumentos seguidas por :
RE_COLON_KEYWORDS = '(%s)' % '|'.join(esc_colon_keywords)
RE_ENDING_KEYWORD = '(%s)' % esc_ending_keywords[0]

# -- CARGOS --
# OR de las palabras clave
RE_CARGOS_KEYWORDS = '(%s)' % '|'.join(CARGO.KEYWORDS)
# RE para capturar el cargo y los nombres
RE_CARGOS_MATCH = RE_CARGOS_KEYWORDS + ':\s([\w+\. ;&]+)+(?:\.$|\.\s)'
# FIXME: algunos nombres pueden contener caracteres raros como &

REGEX1 = re.compile('^(\d+) - (.*?)\.\s*' + RE_ALL_KEYWORDS_NG)
REGEX2 = re.compile('(?=' + RE_ARG_KEYWORDS + '\.\s+(.*?)\.\s*' + RE_ALL_KEYWORDS_NG + ')')
REGEX3 = re.compile(RE_COLON_KEYWORDS + ':\s+(.*?)\.\s*' + RE_ALL_KEYWORDS_NG)
REGEX4 = re.compile(RE_ENDING_KEYWORD + '\.\s+(.*)\.\s*')
REGEX5 = re.compile(RE_NOARG_KEYWORDS + '\.')

REGEX_EMPRESA = re.compile('^(\d+)\s+-\s+(.*)\.$')
REGEX_TEXT = re.compile('^\((.*)\)Tj$')
REGEX_BORME_NUM = re.compile(u'^Núm\. (\d+)', re.UNICODE)
REGEX_BORME_FECHA = re.compile('^\w+ (\d+) de (\w+) de (\d+)')
REGEX_BORME_CVE = re.compile('^cve: (.*)$')


MESES = {'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4, 'mayo': 5, 'junio': 6, 'julio': 7,
         'agosto': 8, 'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12}


# TODO: COOP y otras sociedades menos usuales
# Comprueba si es algún tipo de sociedad o por el contrario es una persona física
def is_company(data):
    siglas = [' SL', ' SA', ' AIE', ' SRL']
    return any(data.endswith(s) for s in siglas)


def regex_empresa(data):
    m = REGEX_EMPRESA.match(data)
    acto_id = int(m.group(1))
    empresa = m.group(2)
    return (acto_id, empresa)


def regex_cargos(data):
    """
    :param data:
    'Adm. Solid.: RAMA SANCHEZ JOSE PEDRO;RAMA SANCHEZ JAVIER JORGE.'
    'Auditor: ACME AUDITORES SL. Aud.Supl.: MACIAS MUÑOZ FELIPE JOSE.'

    :return:

    [('Adm. Solid.', {'RAMA SANCHEZ JOSE PEDRO', 'RAMA SANCHEZ JAVIER JORGE'})]
    [('Auditor', {'ACME AUDITORES SL'}), ('Aud.Supl.', {'MACIAS MUÑOZ FELIPE JOSE'})]
    """
    cargos = []
    for cargo in re.findall(RE_CARGOS_MATCH, data, re.UNICODE):
        cargos.append((cargo[0], set(cargo[1].split(';'))))
    return cargos


# This is a way not to use datetime.strftime, which requires es_ES.utf8 locale generated.
def regex_fecha(data):
    """
    Martes 2 de junio de 2015

    >>> REGEX_BORME_FECHA.match(dd).groups()
    ('2', 'junio', '2015')
    """

    day, month, year = re.match('\w+ (\d+) de (\w+) de (\d+)', data).groups()
    return (int(year), MESES[month], int(day))
