from unittest.mock import patch

import pytest

from mcmd.core import context
from tests.integration.loader_mock import get_dataset_folder
from tests.integration.utils import run_commander, run_commander_fail, random_name


def _ontologies_by_name_query(name):
    return [{
        "field": "ontologyName",
        "operator": "EQUALS",
        "value": name
    }]


@pytest.mark.integration
def test_import_emx(session):
    run_commander('import it_emx_autoid')

    result = session.get('it_emx_autoid_testAutoId')
    assert len(result) > 0

    # cleanup
    session.delete('sys_md_Package', 'it')


@pytest.mark.integration
def test_import_ontology(session):
    run_commander('import uo.owl.zip')

    result = session.get('sys_ont_Ontology', q=_ontologies_by_name_query('uo'))
    assert len(result) == 1

    # cleanup
    session.delete('sys_ont_Ontology', result[0]['id'])


@pytest.mark.integration
def test_import_vcf(session):
    run_commander('import testvcf')

    result = session.get('testvcf')
    assert len(result) == 5

    # cleanup
    session.delete('sys_md_EntityType', 'testvcf')


@pytest.mark.integration
def test_import_vcf_as_name(session):
    name = random_name()
    run_commander('import testvcf --as {}'.format(name))

    result = session.get(name)
    assert len(result) == 5


@pytest.mark.integration
def test_import_fail(capsys):
    run_commander_fail('import broken')


@pytest.mark.integration
def test_import_from_path(session):
    file = get_dataset_folder().joinpath('it_emx_autoid.xlsx')
    run_commander('import --from-path {}'.format(str(file)))

    result = session.get('it_emx_autoid_testAutoId')
    assert len(result) > 0

    # cleanup
    session.delete('sys_md_Package', 'it')


@pytest.mark.integration
def test_import_in_package(session, package):
    run_commander('import testAutoId_unpackaged --in {}'.format(package))

    result = session.get('{}_testAutoId'.format(package))
    assert len(result) > 0


@pytest.mark.integration
def test_import_from_path_in_package(session, package):
    file = get_dataset_folder().joinpath('testAutoId_unpackaged.xlsx')
    run_commander('import --from-path {} --in {}'.format(file, package))

    result = session.get('{}_testAutoId'.format(package))
    assert len(result) > 0


@pytest.mark.integration
@patch('mcmd.io.ask.multi_choice')
def test_import_from_issue(which_file_question, session):
    file_name = 'emx_package-only.xlsx'
    which_file_question.return_value = file_name
    issue_num = 5693
    run_commander('import --from-issue {}'.format(issue_num))

    session.get_by_id('sys_md_Package', 'test')

    # cleanup
    context().get_issues_folder().joinpath(str(issue_num)).joinpath(file_name).unlink()
    session.delete('sys_md_Package', 'test')


@pytest.mark.integration
def test_import_from_issue_named(session):
    file_name = 'emx_package-only.xlsx'
    issue_num = 5693
    run_commander('import --from-issue {} {}'.format(issue_num, file_name))

    session.get_by_id('sys_md_Package', 'test')

    # cleanup
    context().get_issues_folder().joinpath(str(issue_num)).joinpath(file_name).unlink()
    session.delete('sys_md_Package', 'test')


@pytest.mark.integration
def test_import_from_url(session):
    file_url = 'https://github.com/molgenis/molgenis/files/626894/emx_package-only.xlsx'
    run_commander('import --from-url {}'.format(file_url))

    session.get_by_id('sys_md_Package', 'test')

    # cleanup
    session.delete('sys_md_Package', 'test')


@pytest.mark.integration
def test_import_from_git_folder(session, package):
    run_commander('import testAutoId_git --in {}'.format(package))

    result = session.get('{}_testAutoId'.format(package))
    assert len(result) == 4
