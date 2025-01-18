from distutils.core import setup
import py2exe

setup(
    console=['main.py'],
    options={
        'py2exe': {
            'includes': ['colorama', 'requests', 'jinja2', 'dotenv'],
            'bundle_files': 1,
            'optimize': 2,
        }
    },
    data_files=[('', ['.env', 'readme.txt', 'leads.txt', 'Letter.txt'])],
)