from flask import Flask, request, abort
from flask import Flask, request
import json
import gitlab
import jenkins
import requests
from jira import JIRA
from configparser import ConfigParser

config = ConfigParser()
config.read("parametersweb.ini")



app = Flask(__name__)

@app.route('/gitlab',methods=['POST'])
def foo():
   data = json.loads(request.data)
   print("GITLAB Project")
   print (f"Project: {data['project']}\n"
          f"Event: {data['object_kind']}\n\n")

    #push->jenkins build job
   if data['object_kind'] == 'push':
      config_data = config["JENKINS"]
      hostJenkins = config_data['hostjenkins']
      usernameJenkins = config_data['usernamejenkins']
      passwordJenkins = config_data['passwordjenkins']
      server = jenkins.Jenkins(hostJenkins, username=usernameJenkins, password=passwordJenkins)
      #jobs = server.get_jobs()
      #print("JENKINS JOBS")
      #print(jobs)
      job = config_data['job']
      server.build_job(job)
      print("\n")

      #new branch->mergereq
      if data['before'] == '0000000000000000000000000000000000000000':
         config_data1 = config["GITLAB"]
         hostGitlab = config_data1['hostgitlab']
         passwordGitlab = config_data1['passwordgitlab']
         gl = gitlab.Gitlab(url=hostGitlab, private_token=passwordGitlab)
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
      config_data2 = config["JIRA"]
      hostJira = config_data2['hostjira']
      API_token_jira = config_data2['api_token_jira']
      jira = JIRA(hostJira, token_auth=(API_token_jira))
      global new_issue
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
    config_data3 = config["JIRA"]
    hostJira = config_data3['hostjira']
    API_token_jira = config_data3['api_token_jira']
    jira = JIRA(hostJira , token_auth=(API_token_jira))
    #issue_key = config_data3['issue_key']
    if  new_issue:
       issue = jira.issue(new_issue)
       jira.add_comment(issue, data['result'])
       print(f"Jira comment - CREATED - issue->{new_issue}")
    return "OK"


if __name__ == '__main__':
    config_data4 = config["HOST"]
    host = config_data4['host']
    port = config_data4['port']
    app.run(host= host, port= port)
