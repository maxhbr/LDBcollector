""" process_results.py

The goal of this code is to take results produced by *any* avocado test, and
format them to be reported to resultsdb.

Author: Ralph Bean <rbean@redhat.com>
"""

import logging
if __name__ == '__main__':
    # Set up logging ASAP to see potential problems during import.
    # Don't set it up when not running as the main script, someone else handles
    # that then.
    logging.basicConfig()

import json
import os
import shutil

from libtaskotron import check

log = logging.getLogger('modulemd')
log.setLevel(logging.DEBUG)
log.addHandler(logging.NullHandler())

# A lookup that maps avocado result codes with taskotron result codes
status_lookup = {
    'PASS': 'PASSED',
    'WARN': 'NEEDS_INSPECTION',
    'FAIL': 'FAILED',
}


def sanitize(testname):
    """ Take an avocado test name and scrub it...
    ...to make it more suitable to resultsdb's dot-delimited names.
    """
    testname = testname.split('-', 1)[-1]    # Strip off leading 'XX-'
    testname = testname.replace('.py:', '.') # Remove filename suffixes
    testname = testname.rsplit(';run-', 1)[0] # Strip off trailing ';run-XXXX'
    return testname


def run(item, item_type, checkname, workdir='.', artifactsdir='artifacts'):
    '''The main method to run from Taskotron'''

    if not os.path.exists(artifactsdir):
        os.makedirs(artifactsdir)

    workdir = os.path.abspath(workdir)

    # rpms and logs have been downloaded by koji directive and rpmgrill
    # has been prepared and run by run_rpmgrill.sh

    # 1. read in the big results file produced by avocado
    results = read_results(workdir)

    # 2. Store log
    store_logs(workdir, artifactsdir)

    # 3. Massage avocado results into a format suitable for resultsdb/taskotron
    details = list(massage_results(results, checkname, item, item_type, artifactsdir))
    output = check.export_YAML(details)
    return output


def read_results(workdir):
    results_file = os.path.join(workdir, 'latest/results.json')
    with open(results_file, 'r') as f:
        content = f.read()
    return json.loads(content)


def store_logs(workdir, artifactdir):
    log_path = "test-results"

    resultsdir = os.path.join(workdir, 'latest/%s/' % log_path)

    dst_artifactdir = os.path.join(artifactdir, log_path)
    if not os.path.exists(dst_artifactdir):
        os.makedirs(dst_artifactdir)

    # Copy everything in log directory over to be archived.
    for path in os.listdir(resultsdir):
        src = os.path.join(resultsdir, path)
        dst = os.path.join(dst_artifactdir, path)
        if os.path.isfile(src):
            shutil.copyfile(src, dst)
        else:
            shutil.copytree(src, dst)

    # Also, copy a few top-level summary files
    toplevel = os.path.join(workdir, 'latest/')
    for path in os.listdir(toplevel):
        src = os.path.join(toplevel, path)
        if not os.path.isfile(src):
            # Don't copy all the directories at this level..  too much.
            continue
        dst = os.path.join(artifactdir, path)
        shutil.copyfile(src, dst)

    # This is the main file we attach to the check detail
    return os.path.join(artifactdir, 'results.json')


def massage_results(results, checkname, item, item_type, log_path):
    for test in results['tests']:
        outcome = status_lookup.get(test['status'], 'NEEDS_INSPECTION')

        note = test['fail_reason']
        if note == "None":
            note = "No issues found"

        output = [test['whiteboard']]

        detail = check.CheckDetail(
            item=item,
            report_type=item_type,
            outcome=outcome,
            note=note,
            output=output,
            checkname='%s.%s' % (checkname, sanitize(test['id'])),
            artifact=log_path,
        )

        # print some summary to console
        log.info('%s %s for %s (%s)' % (
            detail.checkname, detail.outcome, detail.item, detail.note))

        yield detail

    # Finally, create a wrapper-level CheckResult and tack it on the end.
    if results['errors'] or results['failures']:
        outcome = 'NEEDS_INSPECTION'
        note = "%i issues found" % (results['errors'] + results['failures'])
    else:
        outcome = 'PASSED'
        note = "%i checks passed" % results['pass']

    yield check.CheckDetail(
        item=item,
        report_type=item_type,
        outcome=outcome,
        note=note,
        checkname=checkname,
        artifact=log_path,
    )


if __name__ == '__main__':
    output = run('local-run')
    print output
