import os
import subprocess

class Git():

    @staticmethod
    def stash():
        devnull = open(os.devnull, 'w')
        output = subprocess.check_output(["git", "stash"], stderr=devnull)
        devnull.close()
        return output

    @staticmethod
    def stash_apply():
        devnull = open(os.devnull, 'w')
        subprocess.call(["git", "stash", "apply"], stdout=devnull, stderr=devnull)
        devnull.close()

    @staticmethod
    def stash_pop():
        devnull = open(os.devnull, 'w')
        subprocess.call(["git", "stash", "pop"], stdout=devnull, stderr=devnull)
        devnull.close()

    @staticmethod
    def commit_amend():
        devnull = open(os.devnull, 'w')
        subprocess.call(["git", "commit", "--amend", "--no-edit"], stdout=devnull, stderr=devnull)
        devnull.close()
