#!/usr/bin/env python2
# -*- coding: utf-8 -*-
'''Download the modulemd file, run avocado modulemd validity test and process
the results. This is to be called usually from tests.yml, which can be executed
through Taskotron.'''

import os
import sys
import subprocess
import logging
from libtaskotron.directives import distgit_directive

import process_avocado_results as process

log = logging.getLogger('check_modulemd')
log.setLevel(logging.DEBUG)
log.addHandler(logging.NullHandler())


def split_item(item):
    '''split up dist_git_commit string from namespace/name#gitref to a dict,
    e.g.
    {'namespace': 'modules',
     'name': 'perl',
     'gitref': '943a8626cace15aaf13fb9e498d7be072bd6f3ea'}'''
    namespace, rest = item.split('/', 1)
    name, gitref = rest.split('#', 1)
    return dict(namespace=namespace, name=name, gitref=gitref)

def download_modulemd(namespace, name, gitref, workdir):
    '''Download modulemd file and put it into requested directory.

    :return: path to the downloaded modulemd file
    '''
    localpath = 'download/{}.yaml'.format(name)
    modulemd_file = os.path.abspath(os.path.join(workdir, localpath))
    log.info('Downloading modulemd into {} ...'.format(modulemd_file))

    distgit = distgit_directive.DistGitDirective()
    params = {'package': name,
              'gitref': gitref,
              'namespace': namespace,
              'baseurl': 'https://src.fedoraproject.org',
              'path': [ '{}.yaml'.format(name) ],
              'localpath': [ localpath ],
              'target_dir': workdir,
             }
    arg_data = {'workdir': None}
    distgit.process(params, arg_data)

    log.debug('Downloading complete')
    return modulemd_file

def run_avocado(workdir, modulemd_file):
    '''Run avocado modulemd validity test. Ignore exit code.'''
    log.info('Running avocado...')
    retcode = subprocess.call(
        ['avocado', 'run', 'check_modulemd.py',
         '--job-results-dir', workdir,
         '--mux-inject', 'run:modulemd:{}'.format(modulemd_file)])
    log.info('Avocado run ended with exit code {}'.format(retcode))

def process_results(item, testcase, workdir, artifactsdir):
    '''Process avocado run output, for ResultsDB

    :return: True if all checks passed, False otherwise
    '''
    log.debug('Processing avocado results...')
    all_passed = process.run(item=item, item_type='dist_git_commit',
                             checkname=testcase, workdir=workdir,
                             artifactsdir=artifactsdir)
    log.info('Processing results complete, {}'.format(
        'all checks passed' if all_passed else 'some checks failed'))
    return all_passed

def main():
    logging.basicConfig()
    logging.getLogger('libtaskotron').setLevel(logging.DEBUG)

    item, workdir, artifactsdir, testcase = sys.argv[1:]
    itemdict = split_item(item)

    modulemd_file = download_modulemd(namespace=itemdict['namespace'],
        name=itemdict['name'], gitref=itemdict['gitref'], workdir=workdir)
    run_avocado(workdir=workdir, modulemd_file=modulemd_file)
    all_passed = process_results(item=item, testcase=testcase, workdir=workdir,
                                 artifactsdir=artifactsdir)

    rc = 0 if all_passed else 1
    log.info('Execution complete, exiting with return code {}'.format(rc))
    sys.exit(rc)


if __name__ == '__main__':
    main()
