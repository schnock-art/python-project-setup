#%%
#%%
# Standard Library
import logging
import logging.config
import os
import platform
import re
import shutil
import subprocess
from os.path import expanduser

# setup loggers

config_path = os.path.join(os.path.dirname(__file__), 'logging.conf')
logging.config.fileConfig(config_path, disable_existing_loggers=False)


# This will get the root logger since no logger in the configuration has
# this name.

home = expanduser("~")
# Load environment variables
# (.env is not on git nor project folder, so copilot will not be able to
# find it)

class ProjectSetupManager:
    def __init__(self,
                 new_env_name: str,
                 target_dir:str,
                 if_env_exists: str="use_existing",
                 if_dir_exists: str="use_existing",
                 additional_requirements: str=None
        )->None:
        # get root logger
        # the __name__ resolve to "main" since we are at the root of the project.
        self.logger = logging.getLogger(__name__)

        if_exists_types = ['replace', 'use_existing', 'interrupt']
        if if_env_exists not in if_exists_types:
            raise ValueError("Invalid if_exists type. Expected one of: %s" % if_exists_types)

        if if_dir_exists not in if_exists_types:
            raise ValueError("Invalid if_exists type. Expected one of: %s" % if_exists_types)

        self.if_env_exists = if_env_exists
        self.if_dir_exists = if_dir_exists
        self.new_env_name = new_env_name
        if target_dir is None:
            self.target_dir = os.path.join(os.getcwd(),new_env_name)
        else:
            self.target_dir = target_dir
        self.env_file = 'environment.yml'
        self.requirements_file = 'requirements.txt'
        self.additional_requirements = additional_requirements
        self.source_dir = os.path.join(os.path.dirname(__file__),'new_project_files')

        self.commands = {
            "start_anaconda": "conda activate",
            "conda_activate_env": f"conda activate {self.new_env_name}",
            "create_conda_env": f"conda env create /n {self.new_env_name} -f {self.env_file}",
            "package_install": f"pip install -r {self.requirements_file}",
            "remove_conda_env": f"conda env remove -n {self.new_env_name}",
            "conda_list_envs": "conda env list",
            "init_pre_hook": "pre-commit install"
        }

        if os.path.isdir(self.target_dir):
            self.logger.info(f"Target directory {self.target_dir} already exists.")
            if self.if_dir_exists=='replace':
                self.logger.info(f"Removing target directory {self.target_dir}...")
                shutil.rmtree(self.target_dir)
                self.logger.info(f"Target directory {self.target_dir} removed.")
                os.makedirs(self.target_dir, exist_ok=True)
            elif self.if_dir_exists=='interrupt':
                raise Exception(f"Target directory {self.target_dir} already exists.")
            elif self.if_dir_exists=='use_existing':
                self.logger.info(f"Using existing target directory {self.target_dir}.")
        else:
            self.logger.info(f"Creating target directory {self.target_dir}...")
            os.makedirs(self.target_dir, exist_ok=True)
            self.logger.info(f"Target directory {self.target_dir} created.")
        os.chdir(self.target_dir)


    def check_if_new_env_exists(self):
        get_conda_envs =  subprocess.Popen(self.commands["conda_list_envs"], shell=True, stdout=subprocess.PIPE).stdout
        conda_envs = get_conda_envs.read().decode("utf-8")
        matching_envs=re.findall(rf"\s+{self.new_env_name}\s+",conda_envs)
        if len(matching_envs)>0:
            self.new_env_exists=True
        else:
            self.new_env_exists=False

    def create_conda_environment(self):
        """
        Creates a Conda environment with the given name from the provided environment file.
        """
        try:
            self.logger.info(f'Creating Conda environment {self.new_env_name}...')
            os.system(f"""start /wait cmd /c "{self.commands["create_conda_env"]}" """)
            self.logger.info(f'Conda environment {self.new_env_name} created.')
        except Exception as error:
            self.logger.error(f'Conda environment {self.new_env_name} could not be created.')
            raise error

    def install_packages(self):
        """
        Installs the packages listed in the requirements file.
        """
        try:
            self.logger.info("Installing packages...")
            os.system(f"""start /wait cmd /c "{self.commands["conda_activate_env"]}&{self.commands["package_install"]}" """)
            self.logger.info("Packages installed.")
            if self.additional_requirements is not None:
                self.logger.info("Installing additional packages...")
                os.system(f"""start /wait cmd /c "{self.commands["conda_activate_env"]}&{self.additional_requirements}" """)
                self.logger.info("Additional packages installed.")
        except Exception as error:
            self.logger.error("Packages could not be installed.")
            raise error

    def setup_conda_environment(self):
        """
        Creates a Conda environment with the given name from the provided environment file.
        """
        self.check_if_new_env_exists()
        if self.new_env_exists:
            self.logger.info(f'Conda environment {self.new_env_name} already exists.')
            if self.if_env_exists=='replace':
                self.logger.info(f'Removing Conda environment {self.new_env_name}...')
                os.system(f"""start /wait cmd /c "{self.commands["remove_conda_env"]}" """)
                self.logger.info(f'Conda environment {self.new_env_name} removed.')
                self.create_conda_environment()
            elif self.if_env_exists=='interrupt':
                raise Exception(f'Conda environment {self.new_env_name} already exists.')
            elif self.if_env_exists=='use_existing':
                self.logger.info(f'Using existing Conda environment {self.new_env_name}.')
        self.install_packages()

    def setup_project_files(self):
        """
        Copies the project files from the source directory to the target directory.
        """
        self.logger.info("Setting up project files...")
        #if not os.path.exists(self.target_dir):
        os.makedirs(self.target_dir, exist_ok=True)
        for item in os.listdir(self.source_dir):
            s = os.path.join(self.source_dir, item)
            d = os.path.join(self.target_dir, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                shutil.copy2(s, d)

        self.logger.info("Project files set up.")

    def init_pre_hook(self):
        """
        Method to be run before the main method.
        """
        try:
            self.logger.info("Initializing pre-commit hook...")
            os.system(f"""start /wait cmd /c "{self.commands["conda_activate_env"]}&{self.commands["init_pre_hook"]}" """)
            self.logger.info("Pre-commit hook initialized.")
        except Exception as error:
            self.logger.error("Pre-commit hook could not be initialized.")
            raise error


    def set_up_new_proyect(self):
        self.setup_project_files()
        self.setup_conda_environment()
        self.init_pre_hook()

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Setup a new Python project.')
    parser.add_argument('--new_env_name', type=str, help='Name of the new Conda environment to be created.')
    parser.add_argument('--target_dir', type=str, default=None, help='Target directory for the new project.')
    parser.add_argument('--if_env_exists', type=str, default="interrupt", help='What to do if the Conda environment already exists.')
    parser.add_argument('--if_dir_exists', type=str, default="interrupt", help='What to do if the target directory already exists.')
    parser.add_argument('--additional_requirements', type=str, default=None, help='Additional requirements to be installed.')
    args = parser.parse_args()
    ProjectSetupManager(
        new_env_name=args.new_env_name,
        target_dir=args.target_dir,
        if_env_exists=args.if_env_exists,
        if_dir_exists=args.if_dir_exists,
        additional_requirements=args.additional_requirements
    ).set_up_new_proyect()

if __name__=='__main__':
    main()
