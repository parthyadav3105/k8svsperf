# Copyright 2020 University Of Delhi.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""
Automation of Pod Deployment with Kubernetes Python API
"""

import os
import logging
from jinja2 import Environment, meta, Template

from conf import settings as S
from pods.pod.pod import IPod

class IPodPapi(IPod):
    """
    Class for controlling the pod through PAPI
    """
    def __init__(self):
        """
        Initialisation function.
        """
        super(IPodPapi, self).__init__()
        name, ext = os.path.splitext(S.getValue('LOG_FILE_POD'))
        name = name + str(self._number)
        rename_logs = "{name}_{uid}{ex}".format(name=name,
                                                uid=S.getValue('LOG_TIMESTAMP'),
                                                ex=ext)
        self._logger = logging.getLogger(__name__)
        self._logfile = os.path.join(S.getValue('RESULT_PATH'), rename_logs)
        self._podfile = os.path.join(S.getValue('RESULT_PATH'),
                                     "{name}.yaml".format(name=name))
        self._podtemplate = S.getValue('POD_TEMPLATE')

    def create(self):
        """
        Creation Process
        """
        self._create_pod_definition_file()
        self._cmd = ['sudo', 'kubectl', 'create',
                     '-f='+self._podfile]
        self._logger.info("Creating POD %d ...", self._number)
        super(IPodPapi, self).start()

    def terminate(self):
        """
        Cleanup Process
        """
        self._cmd = ['sudo', 'kubectl', 'delete',
                     '-f='+self._podfile]
        self._logger.info("Terminating POD %d ...", self._number)
        super(IPodPapi, self).start()

    def _get_values(self):
        """
        Returns values of template_varriables as dict
        """
        values = dict()
        with open(self._podtemplate) as templatefile:
            env = Environment()
            template = env.parse(templatefile.read())
            template_variables = meta.find_undeclared_variables(template)
        for var in template_variables:
            values[var] = S.getValue(var)
        return values

    def _render_template(self):
        """
        Renders yaml templates
        """
        with open(self._podtemplate) as templatefile:
            template = Template(templatefile.read())
        return template.render(self._get_values())

    def _create_pod_definition_file(self):
        """
        Generates pod yaml definition file from pod template
        """
        with open(self._podfile, "w") as podfile:
            pod_definition = self._render_template()
            podfile.write(pod_definition)
