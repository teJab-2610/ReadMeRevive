import subprocess
import os

class TreeMaker:
    def __init__(self, FILE_PATH_bf, FILE_PATH_af, OUT_bf, OUT_af,Format):
        self.FILE_PATH_bf = FILE_PATH_bf
        self.FILE_PATH_af = FILE_PATH_af
        self.OUT_bf = OUT_bf
        self.OUT_af = OUT_af
        self.Format = Format

    def generate_AST_trees(self):
        self.generate_trees("ast")

    def generate_CFG_trees(self):
        self.generate_trees("cfg")

    def generate_CDG_trees(self):
        self.generate_trees("cdg")

    def generate_DDG_trees(self):
        self.generate_trees("ddg")

    def generate_PDG_trees(self):
        self.generate_trees("pdg")

    def generate_CPG_trees(self):
        self.generate_trees("cpg14")
    def generate_ALL_trees(self):
        self.generate_trees("all")

    # def generate_trees(self, tree_type):
    #     commands = [
    #         f"joern-parse {self.FILE_PATH_bf}",
    #         f"mkdir -p {self.OUT_bf}",
    #         f"rm -r {self.OUT_bf}/{tree_type}",
    #         f"joern-export --repr={tree_type} --format={self.Format} --out {self.OUT_bf}/{tree_type}",
    #         f"joern-parse {self.FILE_PATH_af}",
    #         f"mkdir -p {self.OUT_af}",
    #         f"rm -r {self.OUT_af}/{tree_type}",
    #         f"joern-export --repr={tree_type} --format={self.Format} --out {self.OUT_af}/{tree_type}"
    #     ]

    #     for cmd in commands:
    #         process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    #         output, error = process.communicate()

    #         if error:
    #             print("Error:", error.decode())
    #         else:
    #             print("Output:", output.decode())


    def generate_trees(self, tree_type):
        commands = [
            f"joern-parse {self.FILE_PATH_bf}",
            f"mkdir -p {self.OUT_bf}",
            f"joern-parse {self.FILE_PATH_af}",
            f"mkdir -p {self.OUT_af}",
        ]

        for cmd in commands:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            output, error = process.communicate()

            # if error:
            #     print("Error:", error.decode())
            # else:
            #     # print("Output:", output.decode())

        # Check if the output directory exists before attempting to remove it
        if os.path.exists(f"{self.OUT_bf}/{tree_type}"):
            rm_command = f"rm -r {self.OUT_bf}/{tree_type}"
            process = subprocess.Popen(rm_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            _, error = process.communicate()

            # if error:
            #     print("Error:", error.decode())

        if os.path.exists(f"{self.OUT_af}/{tree_type}"):
            rm_command = f"rm -r {self.OUT_af}/{tree_type}"
            process = subprocess.Popen(rm_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            _, error = process.communicate()

            # if error:
            #     print("Error:", error.decode())

        export_commands = [
            f"joern-export --repr={tree_type} --format={self.Format} --out {self.OUT_bf}/{tree_type}",
            f"joern-export --repr={tree_type} --format={self.Format} --out {self.OUT_af}/{tree_type}"
        ]

        for export_cmd in export_commands:
            process = subprocess.Popen(export_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            output, error = process.communicate()

            # if error:
            #     print("Error:", error.decode())
            # else:
            #     print("Output:", output.decode())
