import argparse
import importlib
from langumo.configuration import BuildConfig
from langumo.building import (Sequential, ImportFrom, ExportTo,
                              StackOutputs, Parser, ParseRawFile, MergeFiles,
                              ShuffleLines, Residual, TrainTokenizer,
                              TokenizeSentences, SplitValidation)


def _create_parser(name: str) -> Parser:
    module, cls = name[:name.rfind('.')], name[name.rfind('.') + 1:]
    return getattr(importlib.import_module(module), cls)()


def _main():
    parser = argparse.ArgumentParser(
        prog='langumo',
        description='The unified corpus building environment for Language '
                    'Models.')
    parser.add_argument('config', nargs='?', default='build.yml',
                        help='langumo build configuration')
    args = parser.parse_args()

    cfg = BuildConfig(args.config)
    Sequential(
        StackOutputs((
            ImportFrom(arg['path']),
            ParseRawFile(_create_parser(arg['parser']),
                         lang=cfg['build.parsing.language'],
                         min_len=cfg['build.parsing.min-length'],
                         max_len=cfg['build.parsing.max-length'],
                         newline=cfg['build.parsing.newline-token'],
                         num_workers=cfg['build.parsing.num-workers'])
        ) for arg in cfg['inputs']),
        MergeFiles(),

        ShuffleLines(best_seek_cnt=100000, max_buckets=1024),

        Residual(
            ImportFrom(cfg['build.tokenization.prebuilt-vocab'])
            if 'build.tokenization.prebuilt-vocab' in cfg
            else TrainTokenizer(
                vocab_size=cfg['build.tokenization.vocab-size'],
                subset_size=cfg['build.tokenization.subset-size'],
                limit_alphabet=cfg['build.tokenization.limit-alphabet'],
                unk_token=cfg['build.tokenization.unk-token'],
                special_tokens=cfg['build.tokenization.special-tokens']),

            ExportTo(cfg['outputs.vocabulary'])
        ),

        TokenizeSentences(
            unk_token=cfg['build.tokenization.unk-token'],
            special_tokens=cfg['build.tokenization.special-tokens'],
            batch_size=10000),
        SplitValidation(val_ratio=cfg['build.splitting.validation-ratio']),
        ExportTo(cfg['outputs.train-corpus'], cfg['outputs.eval-corpus'])
    ).run(cfg['workspace'])
