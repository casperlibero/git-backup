import argparse
import functools
import git
import json
import jsonpath
import logging
import oauth2
import os
import re
import requests
import urllib

def extract(search, uri):
  logger.debug("Partition search term: '%s'" % search)
  if len(uri) > len(search):
    logger.debug("URI '%s' will be parted by '%s'" % (uri, search))
    base = uri.rpartition(search)
    url = "git@bitbucket.org:%s" % base[len(base) - 1]
    return url
  else:
    logger.error("Zero length URI!")
    return ''

"""
BitBucket SSH URLs
"""
def bitbucket(key, secret):
  logger.debug("Creating oauth2 consumer {'key' : '%s', 'secret' : '%s'}" % (key, secret))
  consumer = oauth2.Consumer(key, secret)
  logger.debug("Creating oauth2 client")
  client = oauth2.Client(consumer)
  url = 'https://api.bitbucket.org/1.0/user/repositories'
  logger.debug("Requesting '%s'..." % url)
  response, content = client.request(url)
  if content != '':
    logger.debug("Loading JSON content...")
    repositories = json.loads(content)
    uris = jsonpath.jsonpath(repositories, '$[*].resource_uri')
    search = '/1.0/repositories/'
    logger.debug("Extracting URIs base after '%s' string..." % search)
    urls = map(functools.partial(extract, search), uris)
    logger.debug("%d URLs found:" % len(urls))
    map(logger.debug, urls)
    return urls
  else:
    logger.error("Could not retrieve the expected JSON content from BitBucket!")
    return [ ]

"""
GitHub SSH URLs
"""
def github(profile, token):
  url = 'https://api.github.com/orgs/%s/repos' % profile
  logger.debug("Requesting '%s' with '%s' token..." % (url, token))
  api_request  = requests.get(url, headers={'Authorization' : 'token %s' % token})
  logger.debug("Loading JSON content...")
  repositories = json.loads(api_request.content)
  if isinstance(repositories, dict) and ('message' in repositories):
    logger.error("Could not retrieve the expected JSON content from GitHub! '%s'" % repositories['message'])
    return [ ]
  logger.debug("Searching for 'clone_url' keys...")
  urls = jsonpath.jsonpath(repositories, '$[*].ssh_url')
  logger.debug("%d URLs found:" % len(urls))
  logger.debug("URLs %s:" % urls)
  map(logger.debug, urls)
  return urls

def mirror(clone_url, dest_dir):
  try:
    repo_dir = os.path.join(dest_dir, os.path.basename(clone_url))
    logger.debug("Cloning '%s' to '%s'..." % (clone_url, repo_dir))
    git.Git().clone(clone_url, repo_dir, mirror=True)
  except Exception as e:
    logger.error('There was an exception: %s' % e)

def fetch(repo_dir):
  try:
    logger.debug("Fetching origin from '%s'..." % repo_dir)
    git.Git(repo_dir).fetch('origin')
  except Exception as e:
    logger.error('There was an exception: %s' % e)

def sync(get_urls, dest_dir):
  urls = get_urls()
  for url in urls:
    if url is not None:
      repo_name = os.path.basename(url)
      repo_dir  = os.path.join(dest_dir, repo_name)
      if os.path.exists(repo_dir):
        fetch(repo_dir)
      else:
        mirror(url, dest_dir)
    else:
      logger.debug('Null URL!')

def get_logger(level):
  FORMAT = '%(asctime)-15s | %(message)s'
  logging.basicConfig(format=FORMAT)
  logger = logging.getLogger('git-backup')
  logger.setLevel(level)
  return logger

def parse_args(parser):
  general_args = parser.add_argument_group("General Options")
  general_args.add_argument('-d', '--dest-dir', dest='dest_dir', help='Destination directory', action='store', required=True)
  general_args.add_argument('-v', '--verbose',  dest='verbose',  help='Verbose mode',          action='store_true')
  bitbucket_args = parser.add_argument_group("BitBucket Options")
  bitbucket_args.add_argument('-k', '--key',    dest='bb_key',    help='OAuth2 Key',    action='store', required=True)
  bitbucket_args.add_argument('-s', '--secret', dest='bb_secret', help='OAuth2 Secret', action='store', required=True)
  github_args = parser.add_argument_group("GitHub Options")
  github_args.add_argument('-p', '--profile', dest='gh_profile', help='Profile', action='store', required=True)
  github_args.add_argument('-t', '--token',   dest='gh_token',   help='Token',   action='store', required=True)
  return parser.parse_args()

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Sync BitBucket and GitHub repositories.')
  args   = parse_args(parser)
  logger = get_logger('DEBUG') if args.verbose else get_logger('INFO')
  logger.debug('Syncing BitBucket...')
  sync(functools.partial(
    bitbucket,
    args.bb_key,
    args.bb_secret,
  ), args.dest_dir)
  logger.debug('Done.')
  logger.debug('Syncing GitHub...')
  sync(functools.partial(
    github,
    args.gh_profile,
    args.gh_token
  ), args.dest_dir)
  logger.debug('Done.')

