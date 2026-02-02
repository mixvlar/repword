import pytest
import os
import subprocess
import time
import sys
import shutil


@pytest.fixture(scope="session", autouse=True)
def flask_server():
    env = os.environ.copy()
    env["TESTING"] = "True"

    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    main_path = os.path.join(root_dir, "main.py")

    proc = subprocess.Popen([sys.executable, main_path], env=env)

    time.sleep(3)
    yield
    proc.terminate()


@pytest.fixture(autouse=True)
def clean_test_db():
    base = os.path.dirname(__file__)
    src = os.path.join(base, "data_template")
    dst = os.path.join(base, "data")

    if os.path.exists(dst):
        shutil.rmtree(dst)

    shutil.copytree(src, dst)
