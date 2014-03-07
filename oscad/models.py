import oscad_data as data

from .exceptions import InvalidLicense

__all__ = ['OSUC', 'LSUC']


class OSUC(object):
    def __init__(self, number, name, description, type, state, form, context,
                 recipient):
        self.number = number
        self.name = name
        self.description = description
        self.type = type
        self.state = state
        self.form = form
        self.context = context
        self.recipient = recipient

    def __str__(self):
        return ('<OSUC {name} t={type} s={state}'
                ' f={form} c={context} r={recipient}>').format(**self.__dict__)

    def __json__(self, request):
        return self.__dict__

    @classmethod
    def from_number(cls, number):
        store = data.osuc[number]

        for candidate in data.licensenames:
            if candidate['osuc'] == number:
                type = candidate['type']
                state = candidate['state']
                form = candidate.get('form', 'any')
                context = candidate['context']
                recipient = candidate['recipient']
                break

        return cls(name=store['name'],
                   number=store['number'],
                   description=store['desc'],
                   type=type,
                   state=state,
                   form=form,
                   context=context,
                   recipient=recipient)

    @classmethod
    def from_attrs(cls, type=None, state=None, form=None, context=None,
                   recipient=None):

        for candidate in data.licensenames:
            t = candidate['type']
            s = candidate['state']
            f = candidate.get('form', form)
            c = candidate['context']
            r = candidate['recipient']

            if (t == type and s == state and f == form and c == context
                    and r == recipient):

                number = candidate['osuc']
                name = 'OSUC-' + number
                desc = data.osuc[number]['desc']

                return cls(name=name,
                           number=number,
                           description=desc,
                           type=type,
                           state=state,
                           form=form,
                           context=context,
                           recipient=recipient)

    def get_lsuc(self, license):

        l = data.licenses.get(license)

        if l is None:
            raise InvalidLicense(license)

        name = l.get(self.number)
        if name is None:
            return None

        return LSUC.from_name(name)


class LicenseInfo(object):
    def __init__(self, name, specification, abbreviation, release):
        self.name = name
        self.specification = specification
        self.abbreviation = abbreviation
        self.release = release

    def __str__(self):
        return '<LicenseInfo {name}>'.format(**self.__dict__)

    def __json__(self, request):
        return self.__dict__


class OSLiCInfo(object):
    def __init__(self, protection, patent, todo, lsuc, explain):
        self.protection = protection
        self.patent = patent
        self.todo = todo
        self.lsuc = lsuc
        self.explain = explain

    def __json__(self, request):
        return self.__dict__


class Requirements(object):
    def __init__(self, req_prefix, notasks, forbids_prefix, forbids_array,
                 mandatory, voluntary):
        self.req_prefix = req_prefix
        self.notasks = notasks
        self.forbids_prefix = forbids_prefix
        self.forbids_array = forbids_array
        self.mandatory = mandatory
        self.voluntary = voluntary

    def __json__(self, request):
        return self.__dict__


class LSUC(object):
    def __init__(self, name, description, license_info, oslic_info,
                 requirements):
        self.name = name
        self.description = description
        self.license_info = license_info
        self.oslic_info = oslic_info
        self.requirements = requirements

    def __str__(self):
        return '<LSUC {name}>'.format(**self.__dict__)

    def __json__(self, request):
        return self.__dict__

    @classmethod
    def from_name(cls, name):
        # why not....
        name = name.replace('PGL', 'PgL')

        store = data.lsuc[name]

        l = store['license']

        license_info = LicenseInfo(name=l['name'],
                                   specification=l['specification'],
                                   abbreviation=l['abbreviation'],
                                   release=l['release'])
        o = store['oslic']

        oslic_info = OSLiCInfo(protection=o['protection'],
                               patent=o['patent'],
                               todo=o['todo'],
                               lsuc=o['lsuc'],
                               explain=o['explain'])

        u = store['usecase']
        name = u['name']
        description = u['desc']

        r = u['requires']

        requirements = Requirements(req_prefix=r['prefix'],
                                    notasks=u['notasks'],
                                    forbids_prefix=u['forbids']['prefix'],
                                    forbids_array=u['forbids']['array'],
                                    mandatory=r.get('man', []),
                                    voluntary=r.get('vol', [])
                                    )

        return cls(name=name, description=description,
                   license_info=license_info, oslic_info=oslic_info,
                   requirements=requirements)
