from setuptools import setup, find_packages


install_requires = [
    "flask==2.0.1",
    "flask_mail==0.9.1",
    "flask_sqlalchemy==2.5.1",
    "psycopg2-binary",
    "bcrypt==3.2.0",
    "flask-restful==0.3.9",
    "flask_migrate==3.0.1",
    "flask_jwt_extended==4.2.3",
    "flask_login==0.5.0",
    "flask_caching==1.10.1",
    "Flask-Babel==2.0.0",
    "raven[flask]",
]

setup(
    name="fardel",
    version="1.4.0",
    description="Complete and modular CMS",
    author="Sepehr Hamzehlouy",
    author_email="s.hamzelooy@gmail.com",
    url="https://github.com/FardelCMS/FardelCMS",
    packages=find_packages(".", exclude=["tests", "tests.*"]),
    include_package_data=True,
    package_data={
        "static": [
            "*.html",
            "*.css",
            "*.ttf",
            "*.eot",
            "*.svg",
            "*.woff",
            "*.woff2",
            "*.otf",
            "*.min.js",
            "*.js",
            "*.js.map",
            "*.gif",
        ],
    },
    install_requires=install_requires,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Programming Language :: Python :: 3.8",
    ],
)
