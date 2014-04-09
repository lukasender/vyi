# -*- coding: utf-8; -*-
import os
import re
import ConfigParser
from setuptools import setup, find_packages

versionf_content = open("vyi/__init__.py").read()
version_rex = r'^__version__ = [\'"]([^\'"]*)[\'"]$'
m = re.search(version_rex, versionf_content, re.M)
if m:
    version = m.group(1)
else:
    raise RuntimeError('Unable to find version string')


def get_versions():
    """picks the versions from version.cfg and returns them as dict"""
    versions_cfg = os.path.join(os.path.dirname(__file__), 'versions.cfg')
    config = ConfigParser.ConfigParser()
    config.optionxform = str
    config.readfp(open(versions_cfg))
    return dict(config.items('versions'))


def nailed_requires(requirements, pat=re.compile(r'^(.+)(\[.+\])?$')):
    """returns the requirements list with nailed versions"""
    versions = get_versions()
    res = []
    for req in requirements:
        if '[' in req:
            name = req.split('[', 1)[0]
        else:
            name = req
        if name in versions:
            res.append('%s==%s' % (req, versions[name]))
        else:
            res.append(req)
    return res


def read(path):
    return open(os.path.join(os.path.dirname(__file__), path)).read()


here = os.path.abspath(os.path.dirname(__file__))
readme = open(os.path.join(here, 'README.md')).read()
changes = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'crate',
    'crash',
    'gevent',
    'lovely.pyrest',
    'pyramid',
    'pyramid_mailer',
]

test_requires = requires + [
]

setup(name='vyi',
      version=version,
      description='vyi',
      long_description='validate your idea',
      classifiers=[
          "Programming Language :: Python",
      ],
      author='Lukas Ender',
      author_email='hello@lukasender.at',
      url='https://github.com/lumannnn/vyi',
      keywords='vyi validate your idea',
      license='apache license 2.0',
      packages=find_packages(),
      namespace_packages=['vyi'],
      include_package_data=True,
      extras_require=dict(
          test=nailed_requires(test_requires),
      ),
      zip_safe=False,
      install_requires=requires,
      tests_require=test_requires,
      test_suite="",
      entry_points={
          'paste.app_factory': [
              'main=vyi.server:app_factory'
          ],
          'paste.server_factory': [
              'server=vyi.green:server_factory',
          ],
          'console_scripts': [
              'app=pyramid.scripts.pserve:main',
          ],
      },
      )
