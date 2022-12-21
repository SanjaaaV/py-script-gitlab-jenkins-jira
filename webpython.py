import json
from configparser import ConfigParser
from flask import Flask, request
import gitlab
import jenkins
import requests
from jira import JIRA


config = ConfigParser()
config.read("parametersweb.ini")


app = Flask(__name__)


@app.route("/gitlab", methods=["POST"])
def gitlab_push_mr():
    data = json.loads(request.data)
    print("GITLAB Project")
    print(f"Project: {data['project']}\n" f"Event: {data['object_kind']}\n\n")

    # push->jenkins build job
    if data["object_kind"] == "push":
        config_data = config["JENKINS"]
        host_jenkins = config_data["hostjenkins"]
        username_jenkins = config_data["usernamejenkins"]
        password_jenkins = config_data["passwordjenkins"]
        server = jenkins.Jenkins(
            host_jenkins, username=username_jenkins, password=password_jenkins
        )
        job = config_data["job"]
        server.build_job(job)
        print("\n")

        # new branch->mergereq
        if data["before"] == "0000000000000000000000000000000000000000":
            config_data1 = config["GITLAB"]
            host_gitlab = config_data1["hostgitlab"]
            password_gitlab = config_data1["passwordgitlab"]
            gl = gitlab.Gitlab(url=host_gitlab, private_token=password_gitlab)
            dataproj = data["project"]
            nameproj = dataproj["name"]
            idproj = dataproj["id"]
            refsplit = data["ref"].split("/")
            branch_name = refsplit[len(refsplit) - 1]
            project = gl.projects.get(idproj)
            project.mergerequests.create(
                {
                    "source_branch": branch_name,
                    "target_branch": "main",
                    "title": "merge from python",
                    "labels": ["label1", "label2"],
                }
            )
            print("New branch - CREATED")
            print(
                f"Merge request - CREATED.\n"
                f"Project: {nameproj}\n"
                f"Branch: {branch_name}\n"
            )

    # mergereq->issue
    elif data["object_kind"] == "merge_request":
        print("\n")
        config_data2 = config["JIRA"]
        host_jira = config_data2["hostjira"]
        api_token_jira = config_data2["api_token_jira"]
        jira = JIRA(host_jira, token_auth=(api_token_jira))
        global new_issue
        new_issue = jira.create_issue(
            project="TES",
            summary="New issue from jira-python",
            description="Look into this one",
            issuetype={"name": "Task"},
        )
        print("Jira issue - CREATED")
        print(new_issue)
    return "OK"


@app.route("/jenkins", methods=["POST"])
def jenkins_issue():
    data = json.loads(request.data)
    print(data["result"])

    # jenkins build-> update issue
    config_data3 = config["JIRA"]
    host_jira = config_data3["hostjira"]
    api_token_jira = config_data3["api_token_jira"]
    jira = JIRA(host_jira, token_auth=(api_token_jira))
    if new_issue:
        issue = jira.issue(new_issue)
        jira.add_comment(issue, data["result"])
        print(f"Jira comment - CREATED - issue->{new_issue}")
    return "OK"


if __name__ == "__main__":
    config_data4 = config["HOST"]
    host = config_data4["host"]
    port = config_data4["port"]
    app.run(host=host, port=port)
