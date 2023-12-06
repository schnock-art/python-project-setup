import os
from unittest.mock import MagicMock, patch

import pytest

from python_project_setup.main import \
    ProjectSetupManager  # Adjust the import according to your file structure


@pytest.fixture
def setup_manager():
    return ProjectSetupManager(
        new_env_name='test-env',
        target_dir='tests/new_python_project',
        if_env_exists='replace',
        additional_requirements=None
    )

def test_check_if_new_env_exists_true(mocker, setup_manager):
    mock_subprocess = mocker.patch('subprocess.Popen')
    mock_subprocess.return_value.stdout.read.return_value = b'\ntest-env\n'
    setup_manager.check_if_new_env_exists()
    assert setup_manager.new_env_exists == True

def test_check_if_new_env_exists_false(mocker, setup_manager):
    mock_subprocess = mocker.patch('subprocess.Popen')
    mock_subprocess.return_value.stdout.read.return_value = b'something something noenv\n'
    setup_manager.check_if_new_env_exists()
    assert setup_manager.new_env_exists == False

def test_create_conda_environment(mocker, setup_manager):
    mocker.patch('os.system', return_value=0)
    setup_manager.create_conda_environment()
    # Assertions to check if environment creation was logged, etc.

def test_install_packages(mocker, setup_manager):
    mocker.patch('os.system', return_value=0)
    setup_manager.install_packages()
    # Assertions to check if package installation was logged, etc.

def test_setup_project_files(mocker, setup_manager):
    # Mocking os.makedirs to avoid actual directory creation
    mock_makedirs = mocker.patch('os.makedirs')

    # Mocking os.listdir to simulate the directory contents
    mocker.patch('os.listdir', return_value=['environment.yml', 'logging.conf', 'main.py', 'Makefile', 'requirements.txt', '__init__.py', 'utilities'])

    # Mocking shutil.copy2 for file copying
    mock_copy2 = mocker.patch('shutil.copy2')

    # Mocking shutil.copytree for directory copying
    mock_copytree = mocker.patch('shutil.copytree')

    # Mocking os.path.isdir to correctly identify directories
    mocker.patch('os.path.isdir', side_effect=lambda x: x == 'utilities')

    # Execute the method
    setup_manager.setup_project_files()

    # Assertions
    mock_makedirs.assert_called_with('tests/new_python_project', exist_ok=True)

    # Check if files are correctly copied
    expected_files = ['environment.yml', 'logging.conf', 'main.py', 'Makefile', 'requirements.txt', '__init__.py']
    for file in expected_files:
        mock_copy2.assert_any_call(os.path.join(setup_manager.source_dir, file), os.path.join('tests/new_python_project', file))


def test_init_pre_hook(mocker, setup_manager):
    mocker.patch('os.system', return_value=0)
    setup_manager.init_pre_hook()
    # Assertions to check if pre-commit hook was initialized, etc.

def test_set_up_new_proyect(mocker, setup_manager):
    mocker.patch.object(setup_manager, 'setup_project_files')
    mocker.patch.object(setup_manager, 'setup_conda_environment')
    mocker.patch.object(setup_manager, 'init_pre_hook')
    setup_manager.set_up_new_proyect()
    setup_manager.setup_project_files.assert_called_once()
    setup_manager.setup_conda_environment.assert_called_once()
    setup_manager.init_pre_hook.assert_called_once()
