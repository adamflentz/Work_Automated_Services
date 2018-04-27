import luigi, json, requests, os
import ntpath
from time import sleep

class CSVValidator(luigi.Task):
    name = luigi.Parameter()
    jsonfile = luigi.Parameter()
    docfile = luigi.Parameter()
    error_limit = luigi.Parameter()
    order_fields = luigi.Parameter()
    token = luigi.Parameter()

    def output(self):
        return luigi.LocalTarget(os.getcwd() + '/tmp/CSV_Validate_%s.json' % self.name)

    def run(self):
        print(self.complete())
        output_file = self.output().open('w')
        files = {}
        data = {}
        headers = {"Authorization": "Token " + self.token}
        files["jsonfile"] = open(self.jsonfile, 'rb')
        files["docfile"] = open(self.docfile, 'rb')
        data["error_limit"] = self.error_limit
        data["order_fields"] = self.order_fields
        r = requests.post('https://eisapi.wm.edu/csvvalidate/',
                          headers=headers,
                          data=data, files=files)
        taskresponse = r.text.encode(encoding="UTF-8")
        taskresponse = json.loads(json.loads(taskresponse))
        json.dump(taskresponse, output_file)
        print("validated")
        output_file.close()

class SchemaGenerator(luigi.Task):
    name = luigi.Parameter()
    csvfile = luigi.Parameter()
    parselines = luigi.Parameter()
    token = luigi.Parameter()

    def output(self):
        return luigi.LocalTarget(os.getcwd() + '/tmp/Schema_Generate_%s.json' % self.name)

    def run(self):
        output_file = self.output().open('w')
        files = {}
        data = {}
        headers = {"Authorization": "Token " + self.token}
        files["csvfile"] = open(self.csvfile, 'rb')
        data["parselines"] = self.parselines
        r = requests.post('https://eisapi.wm.edu/informatica/schema-generate',
                          headers=headers,
                          data=data, files=files)
        taskresponse = r.text.encode(encoding="UTF-8")
        jsontaskdata = json.loads(taskresponse)
        json.dump(jsontaskdata, output_file)
        print("schema generated")
        output_file.close()

class JobStarter(luigi.Task):
    tasktype = luigi.Parameter()
    taskname = luigi.Parameter()
    version = luigi.Parameter()
    token = luigi.Parameter()

    def output(self):
        return luigi.LocalTarget(os.getcwd() + '/tmp/Start_Job_%s.json' % self.taskname)

    def run(self):
        output_file = self.output().open('w')
        data = {}
        headers = {"Authorization": "Token " + self.token}
        data["tasktype"] = self.tasktype
        data["taskname"] = self.taskname
        data["version"] = self.version
        r = requests.post('https://eisapi.wm.edu/informatica/start_job/',
                          headers=headers,
                          data=data)
        taskresponse = r.text.encode(encoding="UTF-8")
        jsontaskdata = json.loads(taskresponse)
        json.dump(jsontaskdata, output_file)
        print("job started")
        output_file.close()

class JobStopper(luigi.Task):
    tasktype = luigi.Parameter()
    taskname = luigi.Parameter()
    version = luigi.Parameter()
    token = luigi.Parameter()

    def output(self):
        return luigi.LocalTarget(os.getcwd() + '/tmp/Stop_Job_%s.json' % self.taskname)

    def run(self):
        output_file = self.output().open('w')
        data = {}
        headers = {"Authorization": "Token " + self.token}
        data["tasktype"] = self.tasktype
        data["taskname"] = self.taskname
        data["version"] = self.versiondjan
        r = requests.post('https://eisapi.wm.edu/informatica/stop_job',
                          headers=headers,
                          data=data)
        taskresponse = r.text.encode(encoding="UTF-8")
        jsontaskdata = json.loads(taskresponse)
        json.dump(jsontaskdata, output_file)
        print("job stopped")
        output_file.close()

class Uploader(luigi.Task):
    name = luigi.Parameter()
    uri = luigi.Parameter()
    path = luigi.Parameter()
    env = luigi.Parameter()
    file = luigi.Parameter()
    md5 = luigi.Parameter()
    token = luigi.Parameter()

    def output(self):
        return luigi.LocalTarget(os.getcwd() + '/tmp/Upload_%s.json' % self.name)

    def run(self):
        output_file = self.output().open('w')
        data = {}
        files = {}
        headers = {"Authorization": "Token " + self.token}
        data["path"] = self.path
        data["env"] = self.env
        files["file"] = open(self.file, 'rb')
        r = requests.post(uri,
                          headers=headers,
                          data=data, files=files)
        taskresponse = r.text.encode(encoding="UTF-8")
        jsontaskdata = json.loads(taskresponse)
        json.dump(jsontaskdata, output_file)
        print("uploaded")
        output_file.close()

class Downloader(luigi.Task):
    name = luigi.Parameter()
    uri = luigi.Parameter()
    path = luigi.Parameter()
    env = luigi.Parameter()
    filename = luigi.Parameter()
    filepath = luigi.Parameter()
    deleteflag = luigi.Parameter()
    outputfile = luigi.Parameter()
    token = luigi.Parameter()
    wait = luigi.IntParameter()

    def output(self):
        return luigi.LocalTarget(os.getcwd() + '/tmp/Download_%s.json' % self.name)

    def run(self):
        sleep(self.wait)
        output_file = self.output().open('w')
        data = {}
        headers = {"Authorization": "Token " + self.token}
        data["path"] = element["Path"]
        data["env"] = element["Env"]
        data["filename"] = element["Filename"]
        data["filepath"] = element["Filepath"]
        data["deleteflag"] = element["Deleteflag"]
        verify = element["Verify"]
        r = requests.post(uri,
                          headers=headers,
                          data=data)
        taskresponse = r.text.encode(encoding="UTF-8")
        jsontaskdata = json.loads(taskresponse)
        json.dump(jsontaskdata, output_file)
        print("downloaded")
        output_file.close()

class Wait(luigi.Task):
    def output(self):
        return luigi.LocalTarget(os.getcwd() + '/tmp/Sleep.json')
    def run(self):
        output_file = self.output().open('w')
        sleep(1)
        slept = {"Slept":"True"}
        json.dump(slept, output_file)
        print("slept")
        output_file.close()

class JSONScheduler(luigi.Task):
    token = luigi.Parameter()
    filepath = luigi.Parameter()
    filedest = luigi.Parameter()
    finallist = []

    # def requires(self):
    #     return {'CSVValidator': CSVValidator(), 'Uploader': Uploader, 'Downloader': Downloader, 'JobStarter': JobStarter, 'JobStopper': JobStopper, 'SchemaGenerator': SchemaGenerator}

    def output(self):
        return luigi.LocalTarget(self.filedest)

    def run(self):
        with open(self.filepath, 'r') as input_file:
            json_string = input_file.read().strip()
            json_dict = json.loads(json_string)
            output = None

            for element in json_dict["jobs"]:
                task_type = element["Type"]
                if task_type == "csv_validate":
                    output = yield CSVValidator(element["name"], element["jsonfile"], element["docfile"], element["errorlimit"],
                                                element["orderfields"], self.token)
                    self.finallist.append(output)
                    print("validated")

                elif task_type == "upload":
                    output = yield Uploader(element["name"], element["URI"], element["Path"], element["Env"], element["File"],
                                            element["MD5"], self.token)
                    self.finallist.append(output)
                    print("uploaded")

                elif task_type == "download":
                    output = yield Downloader(element["name"], element["URI"], element["Env"], element["Filename"], element["Filepath"],
                                              element["Deleteflag"], element["Verify"], self.token, element["Wait"])
                    self.finallist.append(output)
                    print("downloaded")

                elif task_type  == "start_job":
                    output = yield JobStarter(element["Tasktype"], element["Taskname"], element["Version"], self.token)
                    self.finallist.append(output)
                    print("job started")

                elif task_type == "stop_job":
                    output = yield JobStopper(element["Tasktype"], element["Taskname"], element["Version"], self.token)
                    self.finallist.append(output)
                    print("job stopped")

                elif task_type == "generate_schema":
                    output = yield SchemaGenerator(element["name"], element["csvfile"], element["parselines"], self.token)
                    self.finallist.append(output)
                    print("schema generated")

                elif task_type == "sleep":
                    output = yield Wait()

                sleep(0.25)


            output_file = self.output().open('wb')
            output_json = {"tasks": []}
            for element in self.finallist:
                tmp_file = element.open('r')
                file = tmp_file.readlines()
                for items in file:
                    items = json.loads(items)
                    print(items)
                    if items not in output_json["tasks"]:
                        output_json["tasks"].append(items)
            json.dump(output_json, output_file, indent=4, sort_keys=True)
            output_file.close()