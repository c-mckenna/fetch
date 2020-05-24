
import os
from fetch._core import ShellFileProcessor


def test_shellfilepro_required_files_there():
    command = 'ls {base}.py'
    # required_files = (r'^(?P<base>.*test.+)\.py$',['{base}.py','{base}.py'])
    required_files = ('^(?P<base>.*test.+)\\.py$', ['{base}.py', '{base}.py'])
    file_path = os.path.abspath(__file__)
    sfp = ShellFileProcessor(command=command, expect_file=file_path, required_files=required_files)
    sfp.process(file_path)

def test_shellfilepro_required_files_not_there():
    command = 'ls {base}.py'
    required_files = (r'^(?P<base>.*test.+)\.py$', ['{base}.py', '/this/is/not/here/please.py'])
    file_path = os.path.abspath(__file__)
    sfp = ShellFileProcessor(command=command, expect_file=file_path, required_files=required_files)
    sfp.process(file_path)

def test_shellfilepro_required_files_not_there():
    command = 'diff {base} {base}.xml > {base}.xml.diff.txt'
    required_files = ('^(?P<base>.*hdf)', ['{base}', '{base}.xml'])
    file_path = '/home/osboxes/test_data/test_fetch/data/BRDF/MCD43A1.006/2020.05.01/MCD43A1.A2020122.h29v12.006.2020131040947.hdf'
    sfp = ShellFileProcessor(command=command, expect_file=file_path, required_files=required_files)
    sfp.process(file_path)
