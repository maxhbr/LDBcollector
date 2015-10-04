
import os
import os.path
import datetime

# Download rdfhdt from http://www.rdfhdt.org/download/ and then place a
# link to rdf2hdt in bin, e.g.:
#     ln -s ~/usr/hdt-it/trunk/hdt-lib/tools/rdf2hdt bin/
RDF2HDT = 'bin/rdf2hdt'

TODAY = datetime.date.today().isoformat()
env = Environment(ENV = {'PATH' : os.environ['PATH']})


# Generate www/context.jsonld
# ===========================

env.Command('www/context.jsonld', 'data/context.jsonld', 'cp $SOURCE $TARGET')

# Generate www/id/*.txt
# =====================

for f in Glob('upstream/plaintext/*.txt'):
    (basename, suffix) = os.path.splitext(os.path.basename(str(f)))
    output_filename = env.File('www/id/' + basename + '.txt')

    env.Command(output_filename, f, 'cp $SOURCE $TARGET')

# Generate www/id/*.ttl
# =====================

def ttl_output_filename(input_node):
    (basename, suffix) = os.path.splitext(os.path.basename(str(input_node)))

    # Special case our vocabulary
    if basename == 'vocab':
        return env.File('www/ns.ttl')

    return env.File('www/id/' + basename + '.ttl')

TTL_INPUTS = Glob('data/*.ttl')
TTL_OUTPUTS = [ ttl_output_filename(f) for f in TTL_INPUTS ]
CC_TTL_INPUTS = Glob('upstream/rdf/CC-*.rdf')
CC_TTL_OUTPUTS = [ ttl_output_filename(f) for f in CC_TTL_INPUTS ]

env.Append(BUILDERS = {
    'build_turtle': Builder(action = 'src/build/publish.py'),
    'build_turtle_cc': Builder(action = 'src/build/turtle-cc.py')
})

env.build_turtle(TTL_OUTPUTS, TTL_INPUTS)
env.build_turtle_cc(CC_TTL_OUTPUTS, CC_TTL_INPUTS)

# Generate www/id/*.jsonld
# ========================

def ttl_scan(node, env, path):
    # When a .jsonld is built from a .ttl file, we need to have access to www/context.jsonld
    return [ env.File('www/context.jsonld') ]

env.Append(SCANNERS = Scanner(function = ttl_scan, skeys = ['.ttl']))
env.Append(BUILDERS = {
    'build_jsonld': Builder(
        action = 'node src/build/publish-json.js www/context.jsonld $SOURCE $TARGET',
        suffix = '.jsonld',
        src_suffix = '.ttl'
    ),
    'build_vocab_jsonld': Builder(
        action = 'node_modules/.bin/turtle-to-jsonld $SOURCE > $TARGET',
        suffix = '.jsonld',
        src_suffix = '.ttl'
    )
})

for f in TTL_OUTPUTS + CC_TTL_OUTPUTS:
    if str(f) == 'www/ns.ttl':
        env.build_vocab_jsonld(f)
    else:
        env.build_jsonld(f)

# Generate dataset (www/dl/*)
# ===========================

Depends('etc/ldf-server.json', 'www/dl/licensedb.hdt')
env.Command('www/dl/licensedb.ttl', TTL_OUTPUTS + CC_TTL_OUTPUTS, 'src/build/combine.py')
env.Command('www/dl/licensedb.nt', 'www/dl/licensedb.ttl', 'rapper -i turtle $SOURCE > $TARGET')
env.Command('www/dl/licensedb.hdt', 'www/dl/licensedb.nt', RDF2HDT + ' -f ntriples $SOURCE $TARGET')
env.Command('etc/ldf-server.json', 'etc/ldf-server.template.json', 'sed "s/%DATE%/' + TODAY + '/" < $SOURCE > $TARGET')

# Generate website license pages
# ==============================

env.Append(BUILDERS = {
    'build_license_page': Builder(
        action = 'php src/site/license-page.php $SOURCE > $TARGET',
        suffix = '.html',
        src_suffix = '.jsonld'
    ),
})

for f in Glob('www/id/*.jsonld'):
    (basename, suffix) = os.path.splitext(str(f))
    Depends(basename + '.html', [env.File('data/context.jsonld'), Glob('src/site/*.php')])
    env.build_license_page(f)


# www/id/%.html: www/id/%.jsonld data/context.jsonld src/site/license-page.php src/site/metadata.php
# 	@echo Serializing to $@
# 	@php src/site/license-page.php $< > $@


# Generate website
# ================


# ;; Local Variables:
# ;; mode: python
# ;; End:
