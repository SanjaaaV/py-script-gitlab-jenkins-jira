import json
from flask import Flask, request, abort
from flask import Flask, request
import json
import gitlab
import jenkins
import requests
from jira import JIRA


app = Flask(__name__)

@app.route('/gitlab',methods=['POST'])
def foo():
   data = json.loads(request.data)
   print (data)
   print("GITLAB FIRST\n")



   if data['object_kind'] == 'push':
      host = "http://192.168.10.200:8082/"
      usernameJenkins = "svukelic"
      passwordJenkins = "114cf2d71d18de7dd85b1ca7a2ecee0067"
      server = jenkins.Jenkins(host, username=usernameJenkins, password=passwordJenkins)
      response = requests.get("http://192.168.10.200:8082/api/v4/users/svukelic/projects")
      jobs = server.get_jobs()
      print("JENKINS JOBS")
      print(jobs)
      server.build_job('maven2')
      print("uspeh")
      if data['before'] == '0000000000000000000000000000000000000000':
         url = 'http://192.168.10.200:8083/'
         usernameGitlab = "svukelic"
         passwordGitlab = "glpat-xAyPHPx7pJfC2knxNnHx"
         gl = gitlab.Gitlab(url=url, private_token=passwordGitlab)
         dataproj = data['project']
         nameproj = dataproj['name']
         idproj = dataproj["id"]
         refsplit = data['ref'].split("/")
         branchName = refsplit[len(refsplit)-1]
         project = gl.projects.get(idproj)
         project.mergerequests.create({'source_branch': branchName, 'target_branch': 'main', 'title': 'merge cool feature', 'labels':['label1', 'label2']})
         print("NEW BRANCH")
         print (f"Merge request - CREATED.\n"
             f"Project: {nameproj}\n"
             f"Branch: {branchName}\n") 
   elif data['object_kind'] == 'merge_request':
      print("TOPTOP")
      API_token = 'MjE4MTY5NjY3NDQyOi+9u8UDE6TaTjCHGl3otxLiVi2Y'
      username = 'svukelic'
      jira = JIRA('http://192.168.10.200:8086/', token_auth=('API_token'))
      new_issue = jira.create_issue(project='TES', summary='New issue from jira-python', description='Look into this one', issuetype={'name': 'Task'})
   return "OK"


@app.route('/jenkins',methods=['POST'])
def foo1():
   data = json.loads(request.data)
   print (data)
   return "OK"




if __name__ == '__main__':
   app.run(host='192.168.10.200', port='3538')

