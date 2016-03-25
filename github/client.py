#
# All communication with github.com, its remote positories
# or local ones will be carried through this module and alike.
#
# In order to provide replaceable clients (e.g. to switch between
# local and remote repositories) the module will provide various
# classes with the same interface (or with the same subset).
#
# Carried operations:
# - get basic info about repository
# - get a list of branches
# - get a list of commits
# - get info about a commit

import git
import time
import datetime

class GithubClient(object):

	def __init__(self, username, project):
		self.username = username
		self.project = project

	#def branches(self):
		

class GithubLocalClient(object):

	def __init__(self, repo_directory):
		self.repo = git.Repo(repo_directory)
		self.refs = {}

	def branches(self):
		"""Return a list of branches for given repository

		:return: [str]
		"""
		# get all remote branches
		refs = filter(lambda l: isinstance(l, git.RemoteReference), self.repo.references)
		# filter out HEAD branch
		refs = filter(lambda l: l.name != "origin/HEAD", refs)
		# filter out all branches not starting with 'origin/'
		refs = filter(lambda l: l.name.startswith("origin/"), refs)
		for ref in refs:
			self.refs[ref.name[7:]] = ref

		# remove 'origin/' prefix
		return map(lambda l: l.name[7:], refs)

	def _commitData(self, commit):
		"""Get data from a commit object

		:param commit: commit object
		:type  commit: git.objects.commit.Commit
		"""
		return {
			"hexsha": commit.hexsha,
			"adate": commit.authored_date,
			"cdate": commit.committed_date,
			"author": "%s <%s>" % (commit.author.name, commit.author.email),
			"message": commit.message
		}

	# http://stackoverflow.com/questions/9637838/convert-string-date-to-timestamp-in-python
	def commits(self, branch, since = 0, to = time.mktime((datetime.date.today() + datetime.timedelta(hours=24)).timetuple())):
		"""For given branch return a list of commits.
		Each commit contains basic information about itself.

		:param branch: git branch
		:type  branch: [str]{}
		:param since: minimal timestamp for commit's commit date
		:type  since: int
		:param to: maximal timestamp for commit's commit date
		:type  to: int
		"""
		# checkout the branch
		self.repo.create_head(branch, "refs/remotes/origin/%s" % branch)

		since_str = datetime.datetime.fromtimestamp(since).strftime('%Y-%m-%d %H:%M:%S')
		commits = {}
		for commit in self.repo.iter_commits(branch, since=since_str):
			# filter out all commits younger then to
			if commit.committed_date > to:
				continue

			commits[commit.hexsha] = self._commitData(commit)

		return commits

if __name__ == "__main__":
	#client = GithubLocalClient("/home/jchaloup/Packages/golang-github-abbot-go-http-auth/upstream/go-http-auth")
	client = GithubLocalClient("/home/jchaloup/Packages/etcd/upstream/etcd")
	print client.branches()
	print ""
	print len(client.commits("release-2.3").keys())
