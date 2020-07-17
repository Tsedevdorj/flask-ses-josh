from setuptools import setup

def readme():
    with open('README.md', 'w') as f:
        return f.read()

setup(
    name='Flask-SES-Mailer-Josh',
    version='1.0.3',
    url='https://github.com/Tsedevdorj/flask-ses-josh',
    license='Apache2',
    author='Josh Batjargal',
    author_email='tsedevdorj94@gmail.com',
    description='Flask extension to send mail via AWS Simple Email Service.',
    packages=['flask_ses_mailer_josh'],
    zip_safe=False,
    include_package_data=True,
    test_suite='tests',
    platforms='any',
    install_requires=[
        'Flask',
        'boto3'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
