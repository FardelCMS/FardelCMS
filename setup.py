from setuptools import setup, find_packages


install_requires = [
    "flask==1.1.1",
    "flask_mail==0.9.1",
    "flask_sqlalchemy==2.3.2",
    "psycopg2-binary",
    "bcrypt==3.1.4",
    "flask-restful==0.3.6",
    "flask_migrate==2.1.1",
    "flask_jwt_extended==3.8.1",
    "flask-script==2.0.6",
    "flask_login==0.4.1",
    "flask_caching==1.8.0",
    "Flask-Babel==1.0.0",
    "raven[flask]",
]

setup(
    name='fardel',
    version='1.3.0',
    description='Complete and modular CMS',
    author='Sepehr Hamzehlouy',
    author_email='s.hamzelooy@gmail.com',
    url='https://github.com/FardelCMS/FardelCMS',
    packages=find_packages(".", exclude=["tests", "tests.*"]),
    include_package_data=True,
    package_data={
        'static': ['*.html', '*.css', '*.ttf', '*.eot', '*.svg', '*.woff', '*.woff2', '*.otf', '*.js', '*.js.map', '*.gif'],
    },
    install_requires=install_requires,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Programming Language :: Python :: 3.7',
    ],
)
