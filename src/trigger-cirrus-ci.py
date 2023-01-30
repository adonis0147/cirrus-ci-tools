#!/usr/bin/env python3

import argparse
import os
import sys
import cirrus_ci

log = cirrus_ci.Logger().get()

def trigger(arguments):
    ci = cirrus_ci.CirrusCI(arguments.token, arguments.repository, arguments.branch)

    repository_id = ci.get_repository_id()
    log.info('The ID of repository {} is {}'.format(ci.repository, repository_id))

    build_id = ci.create_build(repository_id, arguments.config)
    log.info('Create the Cirrus-CI build successfully, build_id={}, url=http://cirrus-ci.com/build/{}'
             .format(build_id, build_id))

    status = ci.wait_build(build_id, arguments.timeout, arguments.interval)
    if status != 'COMPLETED':
        exit(1)

    task_ids = ci.get_task_ids(build_id)
    log.info('The task IDs of build {} is {}'.format(build_id, task_ids))

    for task_id in task_ids:
        artifact_url = 'https://api.cirrus-ci.com/v1/artifact/task/{}/binary.zip'.format(task_id)
        log.info('The url of the artifact is {}'.format(artifact_url))
        print(artifact_url)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog=os.path.basename(sys.argv[0]))
    parser.add_argument('-t', '--token', help='Cirrus-CI TOKEN', required=True)
    parser.add_argument('-r', '--repository', help='GitHub repository', required=True)
    parser.add_argument('-b', '--branch', help='The branch of the repository', required=True)
    parser.add_argument('-c', '--config', help='The configuration YAML', default='')
    parser.add_argument('-T', '--timeout', help='Timeout (in minutes)', type=int)
    parser.add_argument('-i', '--interval', help='Sleep interval (in seconds)', type=int)
    try:
        args = parser.parse_args()
    except:
        parser.print_help()
        exit(128)

    trigger(args)

