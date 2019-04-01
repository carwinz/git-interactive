import os
import subprocess
import logging

class Git():

    @staticmethod
    def create_repository():
        devnull = open(os.devnull, 'w')
        subprocess.call(["git", "init"], stdout=devnull, stderr=devnull)
        devnull.close()

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

    @staticmethod
    def is_a_git_project():
        try:
            devnull = open(os.devnull, 'w')
            subprocess.check_output(["git", "rev-parse", "--git-dir"], stderr=devnull)
            devnull.close()
            return True
        except subprocess.CalledProcessError as e:
            return False

    @staticmethod
    def remote_branch_configured():
        try:
            devnull = open(os.devnull, 'w')
            output = subprocess.check_output(["git", "config", "--local", "--get", "branch." + Git.current_branch() + ".remote"], stderr=devnull)
            devnull.close()
            return True
        except subprocess.CalledProcessError as e:
            return False

    @staticmethod
    def current_branch():
        devnull = open(os.devnull, 'w')
        output = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], stderr=devnull)
        devnull.close()
        return output.strip()
