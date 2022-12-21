from configparser import ConfigParser

config = ConfigParser()

config["GITLAB"] = {
    "hostGitlab": "http://192.168.10.200:8083/",
    "passwordGitlab": "glpat-xAyPHPx7pJfC2knxNnHx",
}

config["JENKINS"] = {
    "hostJenkins": "http://192.168.10.200:8082/",
    "usernameJenkins": "svukelic",
    "passwordJenkins": "114cf2d71d18de7dd85b1ca7a2ecee0067",
    "job": "maven2",
}

config["JIRA"] = {
    "hostJira": "http://192.168.10.200:8086/",
    "API_token_jira": "OTUwNjA0MDUyNjgxOl7cmORGLvsRpUyI2S7Cj4e5DcJE",
    "issue_key": "TES-1",
}

config["HOST"] = {"host": "192.168.10.200", "port": "3538"}

with open("parametersweb.ini", "w") as f:
    config.write(f)
