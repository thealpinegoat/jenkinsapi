"""
Module for JenkinsInvoke class.
"""


import os
import sys
import logging
import optparse
from typing import Optional

from jenkinsapi import jenkins
from jenkinsapi import __version__ as version


log = logging.getLogger(__name__)


class JenkinsInvoke(object):
    """
    Class to invoke API calls from the command line.
    """

    @classmethod
    @property
    def parser(cls):
        # type: () -> optparse.OptionParser
        """
        The command line argument parser.
        """
        usage = "Usage: %prog [options] jobs <jobs ...>"
        description = (
            "Execute a number of jenkins jobs on the server of your "
            "choice. Optionally block until the jobs are complete."
        )
        parser = optparse.OptionParser(
            usage=usage,
            description=description,
            add_help_option=True,
            version=version,
        )
        DEFAULT_BASEURL = os.environ.get(
            "JENKINS_URL", "http://localhost/jenkins"
        )
        parser.add_option(
            "-J",
            "--jenkinsbase",
            dest="baseurl",
            help="Jenkins server base url. Default: %s" % (DEFAULT_BASEURL,),
            type="str",
            default=DEFAULT_BASEURL,
        )
        parser.add_option(
            "--username",
            "-u",
            dest="username",
            help="Username for jenkins authentication",
            type="str",
            default=None,
        )
        parser.add_option(
            "--password",
            "-p",
            dest="password",
            help="Password for jenkins user authentication",
            type="str",
            default=None,
        )
        parser.add_option(
            "-b",
            "--block",
            dest="block",
            action="store_true",
            default=False,
            help="Block until each of the jobs is complete.",
        )
        parser.add_option(
            "-t",
            "--token",
            dest="token",
            help="Optional security token.",
            default=None,
        )
        return parser

    @classmethod
    def main(cls):
        # type: () -> None
        """
        Command line execution entry point.
        """
        options, jobs = cls.parser.parse_args()
        try:
            try:
                if not jobs:
                    raise RuntimeError("At least one job must be specified!")
            except RuntimeError:
                cls.parser.print_help()
                raise
            cls(options, *jobs)()
        except Exception:
            log.critical("An exception occurred!", exc_info=True)
            sys.exit(1)

    def __init__(self, options, *jobs):
        # type: (optparse.Values, *str) -> None
        """
        Constructor.
        """
        self.options = options
        self.jobs = jobs
        self.api = self._get_api(
            baseurl=options.baseurl,
            username=options.username,
            password=options.password,
        )

    def _get_api(self, baseurl, username, password):
        # type: (str, str, str) -> jenkins.Jenkins
        """
        Returns a helper object for interacting with the Jenkins API.
        """
        return jenkins.Jenkins(baseurl, username, password)

    def __call__(self):
        # type: () -> None
        """
        Invokes all jobs.
        """
        for job in self.jobs:
            self.invoke_job(
                job, block=self.options.block, token=self.options.token
            )

    def invoke_job(self, jobname, block, token):
        # type: (str, bool, Optional[str]) -> None
        """
        Invokes a job.
        """
        type_checks = (
            ("jobname", jobname, str),
            ("block", block, bool),
            ("token", token, Optional[str]),
        )
        for name, value, param_type in type_checks:
            if not isinstance(value, param_type):
                error_message = "%s must be of type %s!"
                raise TypeError(error_message % (name, param_type.__name__))
        job = self.api.get_job(jobname)
        job.invoke(securitytoken=token, block=block)


def main():
    # type: () -> None
    """
    Main function for module.
    """
    logging.basicConfig()
    logging.getLogger("").setLevel(logging.INFO)
    JenkinsInvoke.main()
