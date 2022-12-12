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
   print("\nGITLAB Project")
   print (f"Project: {data['project']}\n"
          f"Event: {data['object_kind']}\n\n")

    #push->jenkins build job
   if data['object_kind'] == 'push':
      host = "http://192.168.10.200:8082/"
      usernameJenkins = "svukelic"
      passwordJenkins = "114cf2d71d18de7dd85b1ca7a2ecee0067"
      server = jenkins.Jenkins(host, username=usernameJenkins, password=passwordJenkins)
      server.build_job('maven2')
      print("\n")

      #new branch->mergereq
      if data['before'] == '0000000000000000000000000000000000000000':
         url = 'http://192.168.10.200:8083/'
         passwordGitlab = "glpat-xAyPHPx7pJfC2knxNnHx"
         gl = gitlab.Gitlab(url=url, private_token=passwordGitlab)
         dataproj = data['project']
         nameproj = dataproj['name']
         idproj = dataproj["id"]
         refsplit = data['ref'].split("/")
         branchName = refsplit[len(refsplit)-1]
         project = gl.projects.get(idproj)
         project.mergerequests.create({'source_branch': branchName, 'target_branch': 'main', 'title': 'merge from python', 'labels':['label1', 'label2']})
         print("New branch - CREATED")
         print (f"Merge request - CREATED.\n"
             f"Project: {nameproj}\n"
             f"Branch: {branchName}\n")

   #mergereq->issue
   elif data['object_kind'] == 'merge_request':
      print("\n")
      API_token_jira = 'OTUwNjA0MDUyNjgxOl7cmORGLvsRpUyI2S7Cj4e5DcJE'
      jira = JIRA('http://192.168.10.200:8086/', token_auth=(API_token_jira))
      new_issue = jira.create_issue(project='TES', summary='New issue from jira-python',
                                    description='Look into this one', issuetype={'name': 'Task'})
      print("Jira issue - CREATED")
      print(new_issue)
   return "OK"


@app.route('/jenkins', methods=['POST'])
def foo1():
    data = json.loads(request.data)
    print(data['result'])

    #jenkins build-> update issue
    API_token_jira = 'OTUwNjA0MDUyNjgxOl7cmORGLvsRpUyI2S7Cj4e5DcJE'
    jira = JIRA('http://192.168.10.200:8086/', token_auth=(API_token_jira))
    issue = jira.issue("TES-1")
    jira.add_comment(issue, data['result'])
    return "OK"


if __name__ == '__main__':
    app.run(host='192.168.10.200', port='3538')

