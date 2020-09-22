from setuptools import dist, setup, find_packages

# `Cython` is used when installing `kss` library.
dist.Distribution().fetch_build_eggs(['Cython'])

setup(
    name='langumo',
    version='0.1.2',

    author='Jungwoo Park',
    author_email='affjljoo3581@gmail.com',

    description='The unified corpus building environment for Language Models.',
    long_description=open('README.md', 'r', encoding='utf-8').read(),
    long_description_content_type='text/markdown',

    keywords=['langumo', 'corpus', 'dataset', 'nlp', 'language-model',
              'deep-learning', 'machine-learning'],
    url='https://github.com/affjljoo3581/Expanda',
    license='Apache-2.0',

    package_dir={'': 'src'},
    packages=find_packages('src'),
    python_requires='>=3.6.0',
    install_requires=[
        'nltk',
        'colorama',
        'pyyaml>=5.3.1',
        'tqdm>=4.46.0',
        'tokenizers>=0.8.0',
        'mwparserfromhell>=0.5.4',
        'kss==1.3.1'
    ],

    entry_points={
        'console_scripts': [
            'langumo = langumo:_main'
        ]
    },

    classifiers=[
        'Environment :: Console',
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ]
)
