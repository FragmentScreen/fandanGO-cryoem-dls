"""
FandanGO DLS Cryo-EM Plugin

Plugin for integrating Diamond Light Source cryo-EM metadata from
SmartEM system into the FandanGO/ARIA workflow.
"""

import core
from fandango_dls.constants import (
    ACTION_GENERATE_METADATA,
    ACTION_SEND_METADATA,
    ACTION_PRINT_PROJECT
)
from fandango_dls.actions import generate_metadata, send_metadata, print_project


class Plugin(core.Plugin):
    """
    FandanGO plugin for DLS Cryo-EM metadata integration

    This plugin extracts metadata from the SmartEM decision system
    and deposits it into ARIA for centralized management.
    """

    @classmethod
    def define_args(cls):
        """Define command-line arguments for each action"""

        cls.define_arg(ACTION_GENERATE_METADATA, {
            'help': {
                'usage': '--acquisition-id ACQUISITION_ID',
                'epilog': '--acquisition-id a1b2c3d4-e5f6-7890-abcd-ef1234567890'
            },
            'args': {
                'acquisition-id': {
                    'help': 'UUID of the SmartEM acquisition to extract metadata from',
                    'required': True
                }
            }
        })

        cls.define_arg(ACTION_SEND_METADATA, {
            'help': {
                'usage': '--visit-id VISIT_ID',
                'epilog': '--visit-id 12345'
            },
            'args': {
                'visit-id': {
                    'help': 'ARIA visit ID to link metadata to',
                    'required': True
                }
            }
        })

    @classmethod
    def define_methods(cls):
        """Map actions to their implementation functions"""

        cls.define_method(ACTION_GENERATE_METADATA, generate_metadata.perform_action)
        cls.define_method(ACTION_SEND_METADATA, send_metadata.perform_action)
        cls.define_method(ACTION_PRINT_PROJECT, print_project.perform_action)
