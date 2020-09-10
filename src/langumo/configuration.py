import yaml
from typing import Dict, Any


_default_configuration = {
    'workspace': 'tmp',
    'outputs': {
        'vocabulary': 'build/vocab.txt',
        'train-corpus': 'build/corpus.train.txt',
        'eval-corpus': 'build/corpus.eval.txt',
    },
    'build': {
        'parsing': {
            'num-workers': 1,
            'language': 'en',
            'newline-token': '[NEWLINE]',
            'min-length': 0,
            'max-length': 1024
        },
        'splitting': {
            'validation-ratio': 0.1
        },
        'tokenization': {
            'subset-size': 1000000000,
            'vocab-size': 32000,
            'limit-alphabet': 1000,
            'unk-token': '[UNK]',
            'special-tokens': ['[START]', '[END]', '[PAD]', '[NEWLINE]']
        }
    }
}


def _update_default_dict(data: Dict, default: Dict):
    for key in default:
        if key not in data:
            data[key] = default[key]
        elif isinstance(data[key], dict) and isinstance(default[key], dict):
            _update_default_dict(data[key], default[key])


class BuildConfig:
    def __init__(self, path: str):
        with open(path, 'r') as fp:
            self.config_dict = yaml.safe_load(fp)

        if 'langumo' not in self.config_dict:
            raise RuntimeError('build configuration file should contain '
                               '`langumo` namespace.')
        self.config_dict = self.config_dict['langumo']

        # Update default configuration values.
        _update_default_dict(self.config_dict, _default_configuration)

    def __getitem__(self, key: str) -> Any:
        current = self.config_dict
        for namespace in key.split('.'):
            current = current[namespace]
        return current

    def __contains__(self, key: str) -> bool:
        current = self.config_dict
        for namespace in key.split('.'):
            if namespace not in current:
                return False
            current = current[namespace]
        return True
