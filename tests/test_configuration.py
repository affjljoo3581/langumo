import os
import tempfile
from langumo.configuration import _update_default_dict, BuildConfig


_dummy_configuration = '''
langumo:
  workspace: tmp

  inputs:
  - path: raw-corpus-1.txt
    parser: raw.corpus.parsers.1
  - path: raw-corpus-2.txt
    parser: raw.corpus.parsers.1
  - path: raw-corpus-2.txt
    parser: raw.corpus.parsers.2

  outputs:
    train-corpus: dliub/txt.niart.suproc
    vocabulary: dliub/txt.bacov

  build:
    parsing:
      num-workers: 6

      min-length: 64
      max-length: 512

    tokenization:
      unk-token: '[UNK]'
      special-tokens:
      - '[START]'
      - '[END]'
      - '[PAD]'
      - '[NEWLINE]'
'''


def test_merging_dictionary_with_default_options():
    original_dict = {
        'key1': 'value1',
        'key3': 'value3',
        'key4': {
            'key1': 'value1',
            'key2': {
                'key1': 'value1'
            }
        }
    }
    default_dict = {
        'key1': 'it would not be overrided.',
        'key2': 'value2',
        'key4': {
            'key2': {
                'key2': 'value2'
            },
            'key3': 'value3'
        },
        'key5': 'value5',
        'key6': {
            'key1': 'value1',
            'key2': {
                'key1': 'value1'
            }
        }
    }

    _update_default_dict(original_dict, default_dict)
    assert original_dict == {
        'key1': 'value1',
        'key2': 'value2',
        'key3': 'value3',
        'key4': {
            'key1': 'value1',
            'key2': {
                'key1': 'value1',
                'key2': 'value2'
            },
            'key3': 'value3'
        },
        'key5': 'value5',
        'key6': {
            'key1': 'value1',
            'key2': {
                'key1': 'value1'
            }
        }
    }


def test_configuration_class_finds_options_well():
    with tempfile.TemporaryDirectory() as tdir:
        config_path = os.path.join(tdir, 'build.yml')
        with open(config_path, 'w') as fp:
            fp.write(_dummy_configuration)

        cfg = BuildConfig(config_path)

        assert 'workspace' in cfg
        assert 'inputs' in cfg
        assert 'outputs.train-corpus' in cfg
        assert 'outputs.eval-corpus' in cfg
        assert 'build.parsing' in cfg
        assert 'build.parsing.num-workers' in cfg
        assert 'build.parsing.language' in cfg
        assert 'build.splitting.validation-ratio' in cfg
        assert 'build.tokenization.subset-size' in cfg
        assert 'build.tokenization.vocab-size' in cfg
        assert 'build.tokenization.unk-token' in cfg

        assert 'foo' not in cfg
        assert 'foo.bar' not in cfg
        assert 'build.foo' not in cfg
        assert 'build.parsing.foo' not in cfg
        assert 'build.foo.bar' not in cfg


def test_configuration_class_get_values_correctly():
    with tempfile.TemporaryDirectory() as tdir:
        config_path = os.path.join(tdir, 'build.yml')
        with open(config_path, 'w') as fp:
            fp.write(_dummy_configuration)

        cfg = BuildConfig(config_path)

        assert cfg['workspace'] == 'tmp'
        assert cfg['outputs.eval-corpus'] == 'build/corpus.eval.txt'
        assert cfg['outputs.vocabulary'] == 'dliub/txt.bacov'
        assert cfg['build.parsing.num-workers'] == 6
        assert cfg['build.parsing.min-length'] == 64
        assert cfg['build.parsing.language'] == 'en'
        assert cfg['build.splitting.validation-ratio'] == 0.1
        assert cfg['build.tokenization.unk-token'] == '[UNK]'
        assert cfg['build.tokenization.vocab-size'] == 32000
