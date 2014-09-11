from __future__ import unicode_literals

from copy import deepcopy

from . import constants
from .client import Client
from .compat import (
    iteritems,
    urljoin
)


class ScrapydAPI(object):
    """
    Provides a thin Pythonic wrapper around the Scrapyd API.
    """

    def __init__(self, target='http://localhost:6800', auth=None,
                 endpoints=None, client=None):
        """
        Instantiates the ScrapydAPI wrapper for use.

        Args:
          target (str): the hostname/port to hit with requests.
          auth (str, str): a 2-item tuple containing user/pass details. Only
                           used when `client` is not passed.
          endpoints: a dictionary of custom endpoints to apply on top of
                     the pre-existing defaults.
          client: a pre-instantiated requests-like client. By default, we use
                  our own client. Override for your own needs.

        """
        if endpoints is None:
            endpoints = {}

        if client is None:
            client = Client()
            client.auth = auth

        self.target = target
        self.client = client
        self.endpoints = deepcopy(constants.DEFAULT_ENDPOINTS)
        self.endpoints.update(endpoints)

    def _build_url(self, endpoint):
        """
        Builds the absolute URL using the target and desired endpoint.
        """
        try:
            path = self.endpoints[endpoint]
        except KeyError:
            msg = 'Unknown endpoint `{0}`'
            raise ValueError(msg.format(endpoint))
        absolute_url = urljoin(self.target, path)
        return absolute_url

    def add_version(self, project, version, egg):
        """
        Adds a new project egg to the Scrapyd service.
        """
        url = self._build_url(constants.ADD_VERSION_ENDPOINT)
        data = {
            'project': project,
            'version': version
        }
        files = {
            'egg': egg
        }
        json = self.client.post(url, data=data, files=files)
        return json['spiders']

    def cancel(self, project, job):
        """
        Cancels a job from a specific project.
        """
        url = self._build_url(constants.CANCEL_ENDPOINT)
        data = {
            'project': project,
            'job': job
        }
        json = self.client.post(url, data=data)
        return True if json['prevstate'] == 'running' else False

    def delete_project(self, project):
        """
        Deletes all versions of a project.
        """
        url = self._build_url(constants.DELETE_PROJECT_ENDPOINT)
        data = {
            'project': project,
        }
        self.client.post(url, data=data)
        return True

    def delete_version(self, project, version):
        """
        Deletes a specific version of a project.
        """
        url = self._build_url(constants.DELETE_VERSION_ENDPOINT)
        data = {
            'project': project,
            'version': version
        }
        self.client.post(url, data=data)
        return True

    def list_jobs(self, project):
        """
        Lists all known jobs.
        """
        url = self._build_url(constants.LIST_JOBS_ENDPOINT)
        params = {'project': project}
        jobs = self.client.get(url, params=params)
        return jobs

    def list_projects(self):
        """
        Lists all deployed projects.
        """
        url = self._build_url(constants.LIST_PROJECTS_ENDPOINT)
        json = self.client.get(url)
        return json['projects']

    def list_spiders(self, project):
        """
        Lists all known spiders for a specific project.
        """
        url = self._build_url(constants.LIST_SPIDERS_ENDPOINT)
        params = {'project': project}
        json = self.client.get(url, params=params)
        return json['spiders']

    def list_versions(self, project):
        """
        Lists all deployed versions of a specific project.
        """
        url = self._build_url(constants.LIST_VERSIONS_ENDPOINT)
        params = {'project': project}
        json = self.client.get(url, params=params)
        return json['versions']

    def schedule(self, project, spider, settings=None, **kwargs):
        """
        Schedules a spider from a specific project to run.
        """

        url = self._build_url(constants.SCHEDULE_ENDPOINT)
        data = {
            'project': project,
            'spider': spider
        }
        data.update(kwargs)
        if settings:
            setting_params = []
            for setting_name, value in iteritems(settings):
                setting_params.append('{0}={1}'.format(setting_name, value))
            data['setting'] = setting_params
        json = self.client.post(url, data=data)
        return json['jobid']