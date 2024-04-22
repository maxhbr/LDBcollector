import oscad_data as data

DUMMY_NUMBER = 0
DUMMY_FUNCTION = 0


def translation(name, default):
    return (DUMMY_NUMBER, DUMMY_FUNCTION,
            name, ['Default: ' + default])


def extract_questions(fileobj, keywords, comment_tags, options):

    for q in data.load_file(fileobj):
        yield (DUMMY_NUMBER, DUMMY_FUNCTION,
               'questions.{}.focus'.format(q['id']),
               ['Default: ' + q['focus']]
               )

        yield (DUMMY_NUMBER, DUMMY_FUNCTION,
               'questions.{}.question'.format(q['id']),
               ['Default: ' + q['question']]
               )

        for c in q['choices']:

            yield (DUMMY_NUMBER, DUMMY_FUNCTION,
                   'questions.{}.choices.{}'.format(q['id'], c['text']),
                   ['Default: ' + c['text']]
                   )


def extract_lsuc(fileobj, keywords, comment_tags, options):
    for name, value in data.load_file(fileobj).items():
        orig_base = 'lsuc.{}.'.format(name)
        base = orig_base

        yield translation(base + 'description', value['usecase']['desc'])

        notasks = value['usecase'].get('notasks')

        if notasks:
            yield translation(base + 'notasks', notasks)

        base = base + 'requires.'

        req = value['usecase']['requires']

        yield translation(base + 'prefix', req['prefix'])

        mandatory = req.get('man')
        if mandatory:
            for num, entry in enumerate(mandatory):
                yield translation(base + 'mandatory.{}'.format(num), entry)

        voluntary = req.get('vol')
        if voluntary:
            for num, entry in enumerate(voluntary):
                yield translation(base + 'voluntary.{}'.format(num), entry)

        base = orig_base + 'forbids.'

        forbids = value['usecase']['forbids']

        yield translation(base + 'prefix', req['prefix'])

        forbids = forbids.get('array')
        if forbids:
            for num, entry in enumerate(forbids):
                yield translation(base + 'array.{}'.format(num), entry)


def extract_osuc(fileobj, keywords, comment_tags, options):
    for k, v in data.load_file(fileobj).items():
        yield (DUMMY_NUMBER, DUMMY_FUNCTION,
               'osuc.{}.description'.format(k),
               ['Default: ' + v['desc']]
               )


def extract_parameters(fileobj, keywords, comment_tags, options):
    for k, v in data.load_file(fileobj).items():
        for p in v:
            for k2, v2 in p.items():
                if v2 == 'id':
                    continue

                yield (DUMMY_NUMBER, DUMMY_FUNCTION,
                       'parameters.{}.{}.{}'.format(k, p['id'], k2),
                       ['Default: ' + v2],
                       )
