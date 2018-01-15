from pkg_resources import resource_stream, resource_string

import yaml


def load_data(name):
    return load_file(resource_stream(__name__, 'data/%s.yml' % name))


def load_file(fileobj):
    return yaml.safe_load(fileobj)

licenses = load_data('licenses')
parameters = load_data('parameters')
licensenames = load_data('licensenames')
osuc = load_data('osuc')
lsuc = load_data('lsuc')
license_details = load_data('license_details')

attrs = [
    ('recipients', 'recipient'),
    ('types', 'type'),
    ('states', 'state'),
    ('forms', 'form'),
    ('contexts', 'context'),
]

valid_inputs = {}

for coll, elem in attrs:
    valid_inputs[elem] = list(set(map(lambda x: x['id'],
                                      parameters[coll])))

valid_licenses = sorted(licenses.keys())

valid_inputs['license'] = valid_licenses

for id, details in license_details.items():
    details['text'] = resource_string(
        __name__, 'data/texts/{}.txt'.format(id)).decode('utf-8')


# generate from sources
def license_matrix():
    return [
        (('proapse', 7), ('unmodified', 3), ('independent', 3),
         ('4yourself', 1), ('any', 1), ('any', 1), '01'),

        (None, None, None,
         ('2others', 2), ('sources', 1), ('any', 1), '02S'),

        (None, None, None,
         None, ('binaries', 1), ('any', 1), '02B'),

        (None, ('modified', 4), ('independent', 4),
         ('4yourself', 2), ('any', 2), ('onlyLocal', 1), '03L'),

        (None, None, None, None, None,
         ('viaInternet', 1), '03N'),

        (None, None, None,
         ('2others', 2), ('sources', 1), ('any', 1), '04S'),

        (None, None, None,
         None, ('binaries', 1), ('any', 1), '04B'),

        (('snimoli', 12), ('unmodified', 6), ('independent', 2),
         ('2others', 2), ('sources', 1), ('any', 1), '05S'),

        (None, None, None,
         None, ('binaries', 1), ('any', 1), '05B'),

        (None, None, ('embedded', 4),
         ('4yourself', 2), ('any', 2), ('onlyLocally', 1), '06L'),

        (None, None, None, None, None,
         ('viaInternet', 1), '06N'),

        (None, None, None,
         ('2others', 2), ('sources', 1), ('any', 1), '07S'),

        (None, None, None,
         None, ('binaries', 1), ('any', 1), '07B'),

        (None, ('modified', 6), ('independent', 2),
         ('2others', 2), ('sources', 1), ('any', 1), '08S'),

        (None, None, None,
         None, ('binaries', 1), ('any', 1), '08B'),

        (None, None, ('embedded', 4),
         ('4yourself', 2), ('any', 2), ('onlyLocally', 1), '09s'),

        (None, None, None, None, None,
         ('viaInternet', 1), '09N'),

        (None, None, None,
         ('2others', 2), ('sources', 1), ('any', 1), '10S'),

        (None, None, None,
         None, ('binaries', 1), ('any', 1), '10B'),
    ]
