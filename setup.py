"""
Установка ZeroTrust Inspector
"""

from setuptools import setup, find_packages
import os

# Читаем README
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

# Читаем requirements
with open('requirements.txt', 'r', encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="zerotrust-inspector",
    version="1.0.0",
    author="Сурнина Ольга Кирилловна",
    author_email="",  # Можно добавить email
    description="Визуализатор и валидатор Zero-Trust политик для домашних сетей и малых офисов",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",  # Можно добавить URL проекта
    packages=find_packages(),
    include_package_data=True,
    package_data={
        '': ['*.qss', '*.j2', '*.yaml', '*.md'],
    },
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'zerotrust-inspector=main:main',
            'zti=run_app:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Security',
        'Topic :: System :: Networking',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: OS Independent',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
    ],
    python_requires='>=3.9',
    keywords='security networking zero-trust iot firewall',
    project_urls={
        'Source': '',  # Можно добавить ссылку на GitHub
        'Documentation': '',  # Можно добавить ссылку на документацию
    },
)
