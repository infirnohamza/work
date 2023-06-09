# -*- coding: utf-8 -*- #
# Copyright 2023 Google LLC. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""The command to disable the Workload Certificate Feature."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.workload_certificate import client
from googlecloudsdk.calliope import base as calliope_base
from googlecloudsdk.command_lib.workload_certificate import resource


class Disable(calliope_base.UpdateCommand):
  """Disable Workload Certificate Feature.

  Disable the Workload Certificate Feature in a fleet.

  ## Examples

  To disable Workload Certificate Feature, run:

    $ {command}
  """

  def Run(self, args):
    feature_name = resource.WorkloadCertificateFeatureResourceName(
        resource.Project()
    )
    return client.WIPClient(self.ReleaseTrack()).DisableFeature(feature_name)
