"""
Takes netID, HW #, and submission # and searches
for the perf.log file in the student submission.
In the perf.log file it will check all test runs
and update the leaderboard as needed.
"""
import psycopg2
import svn.remote
from collections import defaultdict
import re

# getting netID & runID from svn file

def get_test_scores(netID, runID):
	"""
	Gets performance test scores from student submission.

	Arguments:
	netID -- student netID (string)
	runID -- submission # (string)

	Output:
	All performance tests scores in dictionary form
	"""
	scores = {}
	host = svn.remote.RemoteClient('https://svn.rice.edu/r/parsoft/projects/AutoGrader/student-runs/' + netID + '/' + runID + '/' + 'aftergrading/Results/')
	perf = host.cat('performance.txt')
	perf2 = perf.split()
	perf1 = host.cat('grading.properties')
	perf3 = re.split('\W+', perf1)
	for wordex in range(0, len(perf3)):
		if perf3[wordex] == 'assignment':
			homework = perf3[wordex + 1]
			# print perf3[wordex]
			# print homework
			# print "==="
	for word in range(0, len(perf2)):
		if perf2[word] == 'PERF':
			# print 'perf2',perf2
			cores = perf2[word + 1]
			testname = perf2[word + 2]
			extime = perf2[word + 3]
			test = (extime, cores)
			if not testname in scores:
				scores[testname] = [test]
			else:
				scores[testname].append(test)
	return homework, scores


# function for sorting with control variable


CONN = psycopg2.connect('dbname=annachi user=annachi host=localhost')
CUR = CONN.cursor()

def sorting(testame, corecount):

	# CUR.execute("SELECT * FROM spicerack WHERE test_name = %s and core_count = %s ORDER BY execution_time::int limit 10",(testame, corecount))
	CUR.execute("SELECT * FROM spicerack WHERE test_name = %s and core_count = %s ORDER BY execution_time::int",(testame, corecount))
	allstu = CUR.fetchall()
	students = [dict(net_id=row[0], test_name = row[2], execution_time = row[3], core_count = row[4], submission_number = row[5], last_update = row[6]) for row in allstu]
	# student=[dict(net_id=row[0]) for row in allstu]

	return students

