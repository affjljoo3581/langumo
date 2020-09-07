import os
import tqdm
from tokenizers import Tokenizer
from tokenizers.models import WordPiece
from tokenizers.trainers import WordPieceTrainer
from tokenizers.normalizers import BertNormalizer
from tokenizers.pre_tokenizers import BertPreTokenizer
from tokenizers.decoders import WordPiece as WordPieceDecoder
from langumo.building import Builder
from langumo.utils import AuxiliaryFile, AuxiliaryFileManager, colorful
from typing import List

# Enable multi-processing in tokenization.
os.environ['TOKENIZERS_PARALLELISM'] = 'true'


class TrainTokenizer(Builder):
    def __init__(self,
                 vocab_size: int = 32000,
                 subset_size: int = 512000000,
                 limit_alphabet: int = 6000,
                 unk_token: str = '[UNK]',
                 special_tokens: List[str] = []):
        self.vocab_size = vocab_size
        self.subset_size = subset_size
        self.limit_alphabet = limit_alphabet
        self.unk_token = unk_token
        self.special_tokens = special_tokens

    def _create_subset_file(self, afm: AuxiliaryFileManager, af: AuxiliaryFile
                            ) -> AuxiliaryFile:
        subset = afm.create()
        with af.open('rb') as src, subset.open('wb') as dst:
            while True:
                line = src.readline()
                if not line:
                    break

                dst.write(line)

                # If total amount of copied data is more than `subset_size`
                # then stop copying data to the subset file.
                if src.tell() > self.subset_size:
                    break
        return subset

    def build(self, afm: AuxiliaryFileManager, corpus: AuxiliaryFile
              ) -> AuxiliaryFile:
        subset = self._create_subset_file(afm, corpus)

        # Create WordPiece model with a normalizer and pre-tokenizer. Note that
        # BERT-specific normalizer and pre-tokenizer are used in this model.
        tokenizer = Tokenizer(WordPiece())
        tokenizer.normalizer = BertNormalizer(strip_accents=False)
        tokenizer.pre_tokenizer = BertPreTokenizer()

        # Train tokenizer model with subset of corpus.
        trainer = WordPieceTrainer(
            vocab_size=self.vocab_size,
            min_frequency=2,
            show_progress=True,
            limit_alphabet=self.limit_alphabet,
            special_tokens=[self.unk_token] + self.special_tokens,
            continuing_subword_prefix='##')
        tokenizer.train(trainer, [subset.name])

        # Save trained vocabulary to an auxiliary output file.
        vocab = afm.create()
        tokenizer.model.save(os.path.dirname(vocab.name))

        os.rename(os.path.join(os.path.dirname(vocab.name), 'vocab.txt'),
                  vocab.name)

        return vocab


class TokenizeSentences(Builder):
    def __init__(self,
                 unk_token: str,
                 special_tokens: List[str] = [],
                 batch_size: int = 10000):
        self.unk_token = unk_token
        self.special_tokens = special_tokens
        self.batch_size = batch_size

    def _total_lines_in_file(self, af: AuxiliaryFile) -> int:
        total_lines = 0
        with af.open('rb') as fp:
            for _ in fp:
                total_lines += 1
        return total_lines

    def build(self,
              afm: AuxiliaryFileManager,
              corpus: AuxiliaryFile,
              vocab: AuxiliaryFile) -> AuxiliaryFile:
        total_lines = self._total_lines_in_file(corpus)

        # Create WordPiece model and add special tokens. Note that `unk_token`
        # is also a special token.
        tokenizer = Tokenizer(WordPiece(vocab.name, unk_token=self.unk_token))
        tokenizer.add_special_tokens(self.special_tokens + [self.unk_token])

        # Use BERT-specific normalizer, pre-tokenizer and decoder.
        tokenizer.normalizer = BertNormalizer(strip_accents=False)
        tokenizer.pre_tokenizer = BertPreTokenizer()
        tokenizer.decoder = WordPieceDecoder(prefix='##')

        tokenized = afm.create()
        with corpus.open('r') as src, tokenized.open('w') as dst:
            # Create tqdm progress bar with colorful description.
            tqdm_iter = tqdm.tqdm(
                src,
                desc=colorful.render('<r>[*]</r> tokenize sentences with '
                                     '<g>WordPiece</g> model'),
                total=total_lines)

            batch_lines = []
            for line in tqdm_iter:
                batch_lines.append(line)

                # Encode the grouped batch sentences and write the tokenized
                # sentences to the auxiliary output file.
                if len(batch_lines) > self.batch_size:
                    for t in tokenizer.encode_batch(batch_lines):
                        dst.write(' '.join(t.tokens) + '\n')
                    batch_lines.clear()

            # Encode the remainders and write to the output file.
            if batch_lines:
                for t in tokenizer.encode_batch(batch_lines):
                    dst.write(' '.join(t.tokens) + '\n')

        return tokenized
