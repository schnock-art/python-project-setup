#%%
#%%
# Standard Library
import logging
import logging.config
import os
import re
import shutil
import subprocess
from os.path import expanduser
import platform

# setup loggers
logging.config.fileConfig("logging.conf", disable_existing_loggers=False)


# This will get the root logger since no logger in the configuration has
# this name.

home = expanduser("~")
# Load environment variables
# (.env is not on git nor project folder, so copilot will not be able to
# find it)

class ProjectSetupManager:
    def __init__(self, 
                 new_env_name: str, 
                 target_dir:str=r'C:\Users\jange\Python Scripts\test_new_python_proyect', 
                 if_env_exists: str="replace", 
                 additional_requirements: str=None
        )->None:
        # get root logger
        # the __name__ resolve to "main" since we are at the root of the project.
        self.logger = logging.getLogger(__name__)

        if_exists_types = ['replace', 'use_existing', 'interrupt']
        if if_env_exists not in if_exists_types:
            raise ValueError("Invalid if_exists type. Expected one of: %s" % if_exists_types)
        
        self.if_env_exists = if_env_exists
        self.new_env_name = new_env_name
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

        os.chdir(self.target_dir)


    def check_if_new_env_exists(self):
        get_conda_envs =  subprocess.Popen(self.commands["conda_list_envs"], shell=True, stdout=subprocess.PIPE).stdout
        conda_envs = get_conda_envs.read().decode("utf-8")
        matching_envs=re.findall(f"\s+{self.new_env_name}\s+",conda_envs)
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
            os.system(f"""start /wait cmd /c "{self.commands["conda_create_env"]}" """)
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

if __name__=='__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Setup a new Python project.')
    parser.add_argument('--new_env_name', type=str, help='Name of the new Conda environment to be created.')
    parser.add_argument('--target_dir', type=str, help='Target directory for the new project.')
    parser.add_argument('--if_env_exists', type=str, default="replace", help='What to do if the Conda environment already exists.')
    parser.add_argument('--additional_requirements', type=str, default=None, help='Additional requirements to be installed.')
    args = parser.parse_args()
    ProjectSetupManager(
        new_env_name=args.new_env_name, 
        target_dir=args.target_dir, 
        if_env_exists=args.if_env_exists, 
        additional_requirements=args.additional_requirements
    ).set_up_new_proyect()
    