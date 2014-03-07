import yaml
from pkg_resources import resource_stream


def load_data(name):
    return load_file(resource_stream(__name__, 'data/%s.yml' % name))


def load_file(fileobj):
    return yaml.safe_load(fileobj)

licenses = load_data('licenses')
parameters = load_data('parameters')
licensenames = load_data('licensenames')
osuc = load_data('osuc')
lsuc = load_data('lsuc')

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


# generate from sources
def license_matrix():
    return [
        (('proapse', 6), ('unmodified', 3), ('independent', 3),
         ('4yourself', 1), ('any', 1), '01'),

        (None, None, None,
         ('2others', 2), ('sources', 1), '02S'),

        (None, None, None,
         None, ('binaries', 1), '02B'),

        (None, ('modified', 3), ('independent', 3),
         ('4yourself', 1), ('any', 1), '03'),

        (None, None, None,
         ('2others', 2), ('sources', 1), '04S'),

        (None, None, None,
         None, ('binaries', 1), '04B'),

        (('snimoli', 10), ('unmodified', 5), ('independent', 2),
         ('2others', 2), ('sources', 1), '05S'),

        (None, None, None,
         None, ('binaries', 1), '05B'),

        (None, None, ('embedded', 3),
         ('4yourself', 1), ('any', 1), '06'),

        (None, None, None,
         ('2others', 2), ('sources', 1), '07S'),

        (None, None, None,
         None, ('binaries', 1), '07B'),

        (None, ('modified', 5), ('independent', 2),
         ('2others', 2), ('sources', 1), '08S'),

        (None, None, None,
         None, ('binaries', 1), '08B'),

        (None, None, ('embedded', 3),
         ('4yourself', 1), ('any', 1), '09'),

        (None, None, None,
         ('2others', 2), ('sources', 1), '10S'),

        (None, None, None,
         None, ('binaries', 1), '10B'),
    ]
