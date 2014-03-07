import unittest
import requests
import re
import itertools
from pyramid import testing
from pyramid.paster import get_appsettings
from pyramid.i18n import make_localizer, TranslationStringFactory
from bs4 import BeautifulSoup

from oscad.compat import urljoin
from oscad import exceptions


tsf = TranslationStringFactory('oscad')


class DummyRequest(testing.DummyRequest):
    localizer = make_localizer('en', 'oscad:locale')

    def translate(self, *args, **kwargs):
        return self.localizer.translate(tsf(*args, **kwargs))


class UnitTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

        import oscad.views
        self.views = oscad.views
        self.settings = get_appsettings('development.ini#main')
        self.oscad_php = OscadPHP(self.settings['test.oscad_php.url'])

    def tearDown(self):
        testing.tearDown()

    def test_imprint(self):
        request = DummyRequest()
        response = self.views.imprint(request)
        assert response == {}

    def test_change_language(self):
        from pyramid.httpexceptions import HTTPSeeOther

        request = DummyRequest()
        request.cookies['_LOCALE_'] = 'de'
        request.matchdict['lang'] = 'en'

        response = self.views.change_language(request)

        assert isinstance(response, HTTPSeeOther)
        assert response.headers['Set-Cookie'] == '_LOCALE_=en; Path=/'

    def test_default_request(self):
        request = DummyRequest()

        response = self.views.request(request)
        reference_response = self.oscad_php.normal_request_data()

        for q1, q2 in zip(response['questions'],
                          reference_response['questions']):
            assert q1 == q2
        assert response == reference_response

    def test_response(self):
        request_data = self.oscad_php.normal_request_data()

        def make_request(t, c, s, r, f, l):
            req = DummyRequest()
            req.params = {
                'type': t,
                'context': c,
                'state': s,
                'recipient': r,
                'form': f,
                'license': l,
            }

            res = self.views.result(req)

            return res['osuc'].number, res['lsuc'].name

        def extract_choices(name):
            for e in request_data['questions']:
                if e['id'] == name:
                    return list(map(lambda x: x['text'], e['choices']))

        print(request_data)

        types = list(extract_choices('type'))
        contexts = extract_choices('context')
        states = extract_choices('state')
        recipients = extract_choices('recipient')
        forms = extract_choices('form')
        licenses = request_data['licenses']

        perms = itertools.product(types, contexts, states, recipients, forms,
                                  licenses)

        iterations = 0

        for (t, c, s, r, f, l) in perms:
            iterations += 1

            try:
                our_res = make_request(t, c, s, r, f, l)
            except exceptions.InvalidParameterCombination:
                our_res = None

            assert our_res == self.oscad_php.make_request(t, c, s, r, f, l)

        assert iterations == (2**5 * 14)


class OscadPHP(object):
    def __init__(self, baseurl):
        self.baseurl = baseurl
        self.session = requests.Session()

    def make_request(self, t, c, s, r, f, l):
        params = {
            'FocusType': t,
            'FocusContext': c,
            'FocusState': s,
            'FocusRecipient': r,
            'FocusForm': f,
            'FocusLicense': l,
        }
        res = self.session.get(urljoin(self.baseurl,
                                       'fileadmin/php/oscad.php'),
                               params=params)
        soup = BeautifulSoup(res.text)

        if 'Your OSCAd System seems to be set up incorrectly' in res.text:
            return None

        helptext = soup.find('span', id='helpTextId').string.strip()

        osuc_regex = re.compile('.*Open Source Use Case No. ([0-9SB]{2,3}).*')

        match = osuc_regex.match(helptext)
        osuc = match.group(1)

        lsuc_regex = re.compile('^\[=(.{3,5}-\w[\d\w])\]$')
        lsuc_text = soup.find('span', style='font-style:italic').string.strip()
        match = lsuc_regex.match(lsuc_text)
        if match is None:
            print(lsuc_text)
        lsuc = match.group(1)

        return osuc, lsuc

    def make_request_with_osuc(o, l):
        pass

    def normal_request_data(self):

        orig_url = 'en/requests/via-the-oslic-form-sheet.html'
        orig_page = self.session.get(urljoin(self.baseurl, orig_url)).text
        soup = BeautifulSoup(orig_page)

        def license_radiobutton_filter(tag):
            return (tag.name == 'input' and tag['type'] == 'radio' and
                    tag['name'] == 'FocusLicense')

        def find_licenses(status):
            anchor = soup.find(lambda x: x.name == 'td' and x.string == status)
            inner = anchor.parent.find('table', class_='inner')

            for i in inner.find_all(license_radiobutton_filter):
                yield i['value']

        def find_questions():
            def find_choices(root):
                for elem in root.find_all('input'):
                    if elem.get('checked') == 'yes':
                        yield {
                            'text': elem['value'],
                            'default': True,
                        }
                    else:
                        yield {
                            'text': elem['value'],
                        }

            for row in soup.find(
                lambda x: x.get('name') == 'OscadForm').find(
                    'table').find_all('tr', recursive=False)[2:7]:

                raw_focus, raw_question, raw_choices = row.find_all(
                    'td', recursive=False)

                raw_question = ''.join(map(str, raw_question.contents))

                focus = list(raw_focus.stripped_strings)[0]
                question = str(raw_question)
                question = ' '.join(question.split()).strip()
                choices = list(find_choices(raw_choices))
                id_ = raw_choices.find(
                    'input', checked="yes").get("name")[5:].lower()

                yield {
                    'focus': focus,
                    'id': id_,
                    'question': question,
                    'choices': choices,
                }

        default_license = soup.find(lambda x: license_radiobutton_filter(x) and
                                    x.get('checked') == 'yes')['value']
        licenses = sorted(find_licenses('known'))
        planned_licenses = sorted(find_licenses('planned'))
        questions = list(find_questions())

        return {
            'default_license': default_license,
            'licenses': licenses,
            'planned_licenses': planned_licenses,
            'questions': questions,
        }
