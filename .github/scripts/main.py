import os
import glob
import logging

# TO TEST THIS LOCALLY
# export GITHUB_OUTPUT=testyone
# export GITHUB_ENV=testytwo
# export TERRAFORM_MODULES_TEST_OBSERVE_CUSTOMER_LIST="['123578675166', '128872978242']"
# export TEST_DIRECTORY=~/content_eng/k8s/terraform-observe-kubernetes
# python main.py
# should output testyone file with value like:
# directories_with_customerID=["/Users/arthur/content_eng/k8s/terraform-observe-kubernetes/tftests/default_XXXXXX_123578675166", "/Users/arthur/content_eng/k8s/terraform-observe-kubernetes/tftests/gcp_XXXXXX_128872978242", "/Users/arthur/content_eng/k8s/terraform-observe-kubernetes/tftests/min_provider_XXXXXX_123578675166", "/Users/arthur/content_eng/k8s/terraform-observe-kubernetes/tftests/aws_XXXXXX_128872978242", "/Users/arthur/content_eng/k8s/terraform-observe-kubernetes/tftests/all_options_XXXXXX_123578675166"]

PYTHON_LOG_LEVEL = os.getenv("PYTHON_LOG_LEVEL", default="DEBUG")

logging.basicConfig(
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S %z",
    level=PYTHON_LOG_LEVEL,
)


def fast_scandir(dirname):
    subfolders = [f.path for f in os.scandir(dirname) if f.is_dir()]
    for dirname in list(subfolders):
        if "tftests" not in dirname:
            subfolders.extend(fast_scandir(dirname))

    tftests_dirs = []
    for dirname in list(subfolders):
        if "tftests" in dirname and ".terraform" not in dirname:
            tftests_dirs.append(dirname)

    return tftests_dirs


def list_subdirectories(parent_dir, pattern):
    """Returns a list of subdirectories under parent_dir using pattern"""
    logging.debug(f"parent_dir={parent_dir}")
    logging.debug(f"pattern={pattern}")

    subfolders = fast_scandir(parent_dir)
    print("subfolders")
    print(subfolders)

    glob_dirs = []
    subdirectories = []
    # Create the glob pattern to match subdirectories
    for subfolder in subfolders:
        glob_dirs.append(os.path.join(subfolder, pattern))
    # Use glob to find subdirectories matching the pattern
    for dir in glob_dirs:
        subdirectories = subdirectories + glob.glob(dir, recursive=True)
    # Filter out files from the list
    subdirectories = [
        directory for directory in subdirectories if os.path.isdir(directory)
    ]

    return subdirectories


def pick_my_env(ENVS, DIRS):
    """Adds a customerID for each script to accomplish round robin"""
    envs_count = len(ENVS)
    # use this for validation purposes
    envs_list = []

    env_index = 0
    for dir in DIRS:
        concat_string = f"{dir}_XXXXXX_{ENVS[env_index]}"
        concat_string = concat_string.replace(" ", "").replace("'", "")
        envs_list.append(concat_string)
        print("-----------------")
        print("dir = ", dir)

        print("env = ", ENVS[env_index])
        env_index += 1

        if env_index > envs_count - 1:
            env_index = 0
        print("-----------------")

    # need this form to write to file
    envs_list_range = f"""[{", ".join(f'"{item}"' for item in envs_list)}]"""
    return envs_list, envs_list_range


def split_string_into_dir_and_customer(string_to_split, delimiter="_XXXXXX_"):
    split_list = string_to_split.split(delimiter)
    if len(split_list) != 2:
        raise ValueError(f"Bad string value: {string_to_split}")

    # write to Github Actions GITHUB_ENV file
    with open(os.environ["GITHUB_ENV"], "a") as ge:
        print(f"TEST_DIR={split_list[0]}", file=ge)
        print(f"CUST_NUMBER={split_list[1]}", file=ge)

    return None


if __name__ == "__main__":

    # Github actions environment variable
    GITHUB_OUTPUT = os.getenv("GITHUB_OUTPUT")
    GITHUB_ENV = os.getenv("GITHUB_ENV")
    # Comma separated list of customer ids for staging environment that are used to runs tftests - provided as a secret
    TEST_CUSTOMER_IDS = (
        os.getenv("TERRAFORM_MODULES_TEST_OBSERVE_CUSTOMER_LIST")
        .replace("[", "")
        .replace("]", "")
    )

    # Split back into python list
    ENVS = TEST_CUSTOMER_IDS.split(",")

    # Example usage:
    parent_directory = os.getenv("TEST_DIRECTORY") or os.getcwd()
    pattern = "*"  # Match all directories

    subdirectories = list_subdirectories(parent_directory, pattern)
    envs_list, envs_list_range = pick_my_env(ENVS, subdirectories)

    # write to Github Actions GITHUB_OUTPUT file
    with open(os.environ["GITHUB_OUTPUT"], "a") as fh:
        print(f"directories_with_customerID={envs_list_range}", file=fh)

    # Print out for validation
    i = 0
    for dir in envs_list:
        print(dir)
        split_str = dir.split("_XXXXXX_")
        print(split_str[0])
        print(split_str[1])
        i += 1
