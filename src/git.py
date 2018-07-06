import os
import subprocess
from subprocess import check_output

class Git():

    @staticmethod
    def stash():
        devnull = open(os.devnull, 'w')
        output = subprocess.check_output(["git", "stash"], stderr=devnull)
        devnull.close()
        return output

    @staticmethod
    def stash_apply():
        Git.execute_suppressing_output(["git", "stash", "apply"])

    @staticmethod
    def stash_pop():
        Git.execute_suppressing_output(["git", "stash", "pop"])

    @staticmethod
    def commit_amend():
        Git.execute_suppressing_output(["git", "commit", "--amend", "--no-edit"])

    @staticmethod
    def current_branch():
        branches = check_output(["git", "branch"]).splitlines()
        branch = [x for x in branches if x.startswith("*")][0]
        return branch[2:]

    @staticmethod
    def has_remote_branch():
        try:
            remote = check_output(["git", "config", "branch.\"" + Git.current_branch() + "\".remote" ])
            return True
        except subprocess.CalledProcessError as grepexc:
            return False

    @staticmethod
    def execute_suppressing_output(command_array):
        devnull = open(os.devnull, 'w')
        subprocess.call(command_array, stdout=devnull, stderr=devnull)
        devnull.close()
