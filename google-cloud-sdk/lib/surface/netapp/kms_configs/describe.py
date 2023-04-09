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
"""Describes a Cloud NetApp Volumes KMS Config."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.netapp.kms_configs import client as kmsconfigs_client
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.netapp import flags
from googlecloudsdk.command_lib.util.concepts import concept_parsers


@base.Hidden
@base.ReleaseTracks(base.ReleaseTrack.BETA)
class DescribeBeta(base.DescribeCommand):
  """Show metadata for a Cloud NetApp Volumes KMS Config."""

  detailed_help = {
      'DESCRIPTION': """\
          Describe a KMS (Key Management System) Config
          """,
      'EXAMPLES': """\
          The following command gets metadata using describe for a KMS Config instance in the default netapp/location

              $ {command}

          To get metadata on a KMS Config in a specified location, run:

              $ {command} --location=us-central1
          """,
  }

  _RELEASE_TRACK = base.ReleaseTrack.BETA

  @staticmethod
  def Args(parser):
    concept_parsers.ConceptParser([flags.GetKmsConfigPresentationSpec(
        'The KMS Config to describe.')]).AddToParser(parser)

  def Run(self, args):
    """Run the describe command."""
    kmsconfig_ref = args.CONCEPTS.kms_config.Parse()
    client = kmsconfigs_client.KmsConfigsClient(
        release_track=self._RELEASE_TRACK)
    return client.GetKmsConfig(kmsconfig_ref)
