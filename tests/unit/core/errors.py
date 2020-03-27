import unittest
from unittest.mock import patch

import pytest

from mcmd.core.errors import McmdError, ScriptError, ConfigError, MolgenisOfflineError


@pytest.mark.unit
class ErrorsTest(unittest.TestCase):

    @staticmethod
    def test_mcmd_error():
        try:
            raise McmdError("test message")
        except McmdError as e:
            assert e.message == "test message"
            assert e.info is None

    @staticmethod
    def test_mcmd_error_info():
        try:
            raise McmdError("test message", info="don't use it like that")
        except McmdError as e:
            assert e.message == "test message"
            assert e.info is "don't use it like that"

    @staticmethod
    def test_mcmd_script_error():
        try:
            raise ScriptError("test message", info="don't use it like that", line=3)
        except ScriptError as e:
            assert e.message == "test message"
            assert e.info is "don't use it like that"
            assert e.line == 3

    @staticmethod
    def test_mcmd_script_error_wrapped():
        try:
            error = McmdError("test message", info="don't use it like that")
            raise ScriptError.from_error(error, line=3)
        except ScriptError as e:
            assert e.message == "test message"
            assert e.info is "don't use it like that"
            assert e.line == 3

    @staticmethod
    def test_mcmd_config_error():
        try:
            raise ConfigError("test message")
        except McmdError as e:
            assert e.message == "There's an error in the configuration file: test message"
            assert e.info is None

    @staticmethod
    @patch("mcmd.config.config.url")
    def test_mcmd_molgenis_offline_error(url):
        url.return_value = "http://localtoast"
        try:
            raise MolgenisOfflineError()
        except McmdError as e:
            assert e.message == "Can't connect to http://localtoast"
            assert e.info is None
