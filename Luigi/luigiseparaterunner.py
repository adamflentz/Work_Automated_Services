import luigi, json, requests

class CSVValidator(luigi.Task):
    jsonfile = luigi.Parameter()
    docfile = luigi.Parameter()
    error_limit = luigi.Parameter()
    order_fields = luigi.Parameter()
    output_file = luigi.Parameter()
    header = luigi.DictParameter()

    def output(self):
        return luigi.LocalTarget(self.output_file)

    def run(self):
        output_file = self.output().open('w')
        files = {}
        data = {}
        files["jsonfile"] = open(self.jsonfile, 'rb')
        files["docfile"] = open(self.docfile, 'rb')
        data["error_limit"] = self.error_limit
        data["order_fields"] = self.order_fields
        r = requests.post('https://eisapi.wm.edu/csvvalidate/',
                          headers=headers,
                          data=data, files=files)
        taskresponse = r.text.encode(encoding="UTF-8")
        print type(taskresponse)
        print(taskresponse)
        jsontaskdata = json.loads(taskresponse)
        json.dump(jsontaskdata, output_file)
        print("validated")
        output_file.close()

class SchemaGenerator(luigi.Task):
    csvfile = luigi.Parameter()
    parselines - luigi.Parameter()
    output_file = luigi.Parameter()
    header = luigi.DictParameter()

    def output(self):
        return luigi.LocalTarget(self.output_file)

    def run(self):
        output_file = self.output().open('w')
        files = {}
        data = {}
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
    output_file = luigi.Parameter()
    header = luigi.DictParameter()

    def output(self):
        return luigi.LocalTarget(self.output_file)

    def run(self):
        output_file = self.output().open('w')
        data = {}
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
    output_file = luigi.Parameter()
    header = luigi.DictParameter()

    def output(self):
        return luigi.LocalTarget(self.output_file)

    def run(self):
        output_file = self.output().open('w')
        data = {}
        data["tasktype"] = self.tasktype
        data["taskname"] = self.taskname
        data["version"] = self.version
        r = requests.post('https://eisapi.wm.edu/informatica/stop_job',
                          headers=headers,
                          data=data)
        taskresponse = r.text.encode(encoding="UTF-8")
        jsontaskdata = json.loads(taskresponse)
        json.dump(jsontaskdata, output_file)
        print("job stopped")
        output_file.close()

class Uploader(luigi.Task):
    uri = luigi.Parameter()
    path = luigi.Parameter()
    env = luigi.Parameter()
    file = luigi.Paramater()
    md5 = luigi.Parameter()
    header = luigi.DictParameter()

    def output(self):
        return luigi.LocalTarget(self.outputfile)

    def run(self):
        output_file = self.output().open('w')
        data = {}
        files = {}
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
    uri = luigi.Parameter()
    path = luigi.Parameter()
    env = luigi.Parameter()
    filename = luigi.Parameter()
    filepath = luigi.Parameter()
    deleteflag = luigi.Parameter()
    outputfile = luigi.Parameter()
    header = luigi.DictParameter()

    def output(self):
        return luigi.LocalTarget(self.outputfile)

    def run(self):
        output_file = self.output().open('w')
        data = {}
        data["path"] = element["Path"]
        data["env"] = element["Env"]
        data["filename"] = element["Filename"]
        data["filepath"] = element["Filepath"]
        data["deleteflag"] = element["Deleteflag"]
        verify = element["Verify"]
        r = requests.post(uri,
                          headers=self.headers,
                          data=data)
        taskresponse = r.text.encode(encoding="UTF-8")
        jsontaskdata = json.loads(taskresponse)
        json.dump(jsontaskdata, output_file)
        print("downloaded")
        output_file.close()

class JSONScheduler(luigi.Task):
    token = luigi.Parameter()
    filepath = luigi.Parameter()
    filedest = luigi.Parameter()

    def output(self):
        return luigi.LocalTarget(self.filedest)

    def run(self):
        with open(self.filepath, 'r') as input_file:
            json_string = input_file.read().strip()

            for element in json_dict["jobs"]:
                headers = {"Authorization": "Token " + self.token}
                task_type = element["Type"]

                if task_type == "csv_validate":
                    output = yield CSVValidator(element["jsonfile"], element["docfile"], element["error_limit"],
                                                element["order_fields"], output_file, headers)
                    print("validated")

                elif task_type == "upload":
                    output = yield Uploader(element["URI"], element["Path"], element["Env"], element["File"],
                                            element["MD5"], headers)
                    print("uploaded")

                elif task_type == "download":
                    output = yield Downloader(element["URI"], element["Env"], element["Filename"], element["Filepath"],
                                              element["Deleteflag"], element["Verify"], output_file, headers)
                    print("downloaded")

                elif task_type  == "start_job":
                    output = yield JobStarter(element["Tasktype"], element["Taskname"], element["Version"], output_file,
                                              headers)
                    print("job started")

                elif task_type == "stop_job":
                    output = yield JobStopper(element["Tasktype"], element["Taskname"], element["Version"], output_file,
                                              headers)
                    print("job stopped")

                elif task_type == "generate_schema":
                    output = yield SchemaGenerator(element["csvfile"], element["parselines"], output_file, headers)
                    print("schema generated")
            print(output_file)