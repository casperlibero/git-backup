import requests, json, re, git, shutil, urllib


"""
Bitbucket
"""

git_vendor          = "bitbucket"
api_endpoint        = "https://api.bitbucket.org"
api_username        = "SET_YOUR_BITBUCKET_USERNAME_HERE"
api_password        = "SET_YOUR_BITBUCKET_PASSWORD_HERE"
repository_http_url = "https://" + urllib.quote(api_username) + ":" + urllib.quote(api_password) + "@bitbucket.org/\\1/\\2.git"


repositories_url = api_endpoint + "/1.0/user/repositories?format=json"
req = requests.get(repositories_url, auth=(api_username, api_password))
repositories = json.loads(req.content)

for repository in repositories:

  git_repository = re.sub("\/1.0\/repositories\/([^\/]+)\/([^\/]+)", repository_http_url, repository['resource_uri'])
  git_repository_name = re.sub("\/1.0\/repositories\/([^\/]+)\/([^\/]+)", "\\2.git" , repository['resource_uri'])

  try:
    print "removing old " + git_repository_name
    shutil.rmtree(git_repository_name)
  except:
    print "not found, skipped"

  print "cloning " + git_repository_name + " from " + git_vendor
  git.Git().clone(git_repository, bare=True)

  git_repository_dir = git_vendor + "/" + git_repository_name

  try:
    print "removing old " + git_repository_dir
    shutil.rmtree(git_repository_dir)
  except:
    print "not found, skipped"

  print "moving new " + git_repository_name + " to " + git_repository_dir
  shutil.move(git_repository_name, git_repository_dir)


"""
GitHub
"""

git_vendor          = "github"
api_endpoint        = "https://api.github.com"
api_account         = "casperlibero"
api_username        = "SET_YOUR_GITHUB_USERNAME_HERE"
api_password        = "SET_YOUR_GITHUB_PASSWORD_HERE"
repository_http_url = "https://" + urllib.quote(api_username) + ":" + urllib.quote(api_password) + "@github.com/\\1/\\2.git"


repositories_url = api_endpoint + "/orgs/" + api_account + "/repos"
req = requests.get(repositories_url, auth=(api_username, api_password))
repositories = json.loads(req.content)

for repository in repositories:

  git_repository = re.sub("github.com", urllib.quote(api_username) + ":" + urllib.quote(api_password) + "@github.com", repository['clone_url'])
  git_repository_name = repository['name'] + ".git"

  try:
    print "removing old " + git_repository_name
    shutil.rmtree(git_repository_name)
  except:
    print "not found, skipped"

  print "cloning " + git_repository_name + " from " + git_vendor
  git.Git().clone(git_repository, bare=True)

  git_repository_dir = git_vendor + "/" + git_repository_name

  try:
    print "removing old " + git_repository_dir
    shutil.rmtree(git_repository_dir)
  except:
    print "not found, skipped"

  print "moving new " + git_repository_name + " to " + git_repository_dir
  shutil.move(git_repository_name, git_repository_dir)
