import torch
import numpy as np


def construct_collate_fn(feature_type, use_shortlist=False):
    def _collate_fn_dense_full(batch):
        return collate_fn_dense_full(batch)

    def _collate_fn_dense_sl(batch):
        return collate_fn_dense_sl(batch)

    def _collate_fn_sparse_full(batch):
        return collate_fn_sparse_full(batch)

    def _collate_fn_sparse_sl(batch):
        return collate_fn_sparse_sl(batch)

    if feature_type == 'dense':
        if use_shortlist:
            return _collate_fn_dense_sl
        else:
            return _collate_fn_dense_full
    else:
        if use_shortlist:
            return _collate_fn_sparse_sl
        else:
            return _collate_fn_sparse_full


def collate_fn_sparse_sl(batch):
    """
        Combine each sample in a batch with shortlist
        For sparse features
    """
    batch_data = {}
    batch_size = len(batch)
    seq_lengths = [len(item[0][0]) for item in batch]
    batch_data['X'] = torch.zeros(batch_size, max(seq_lengths)).long()
    batch_data['X_w'] = torch.zeros(batch_size, max(seq_lengths))
    sequences = [item[0] for item in batch]
    for idx, (seq, seqlen) in enumerate(zip(sequences, seq_lengths)):
        batch_data['X'][idx, :seqlen] = torch.LongTensor(seq[0])
        batch_data['X_w'][idx, :seqlen] = torch.FloatTensor(seq[1])
    shortlist_size = len(batch[0][1][0])
    batch_data['Y_s'] = torch.zeros(batch_size, shortlist_size).long()
    batch_data['Y'] = torch.zeros(batch_size, shortlist_size)
    batch_data['Y_d'] = torch.zeros(batch_size, shortlist_size)
    sequences = [item[1] for item in batch]
    for idx, seq in enumerate(sequences):
        batch_data['Y_s'][idx, :] = torch.LongTensor(seq[0])
        batch_data['Y'][idx, :] = torch.FloatTensor(seq[1])
        batch_data['Y_d'][idx, :] = torch.FloatTensor(seq[2])
    batch_data['batch_size'] = batch_size
    return batch_data

def collate_fn_dense_sl(batch):
    """
        Combine each sample in a batch with shortlist
        For dense features
    """
    batch_data = {}
    batch_size = len(batch)
    emb_dims = batch[0][0].size
    batch_data['X'] = np.zeros((batch_size, emb_dims))
    for idx, _batch in enumerate(batch):
        batch_data['X'][idx, :] = _batch[0]
    batch_data['X'] = torch.from_numpy(batch_data['X']).type(torch.FloatTensor)

    shortlist_size = len(batch[0][1][0])
    batch_data['Y_s'] = torch.zeros(batch_size, shortlist_size).long()
    batch_data['Y'] = torch.zeros(batch_size, shortlist_size)
    batch_data['Y_d'] = torch.zeros(batch_size, shortlist_size)
    sequences = [item[1] for item in batch]
    for idx, seq in enumerate(sequences):
        batch_data['Y_s'][idx, :] = torch.LongTensor(seq[0])
        batch_data['Y'][idx, :] = torch.FloatTensor(seq[1])
        batch_data['Y_d'][idx, :] = torch.FloatTensor(seq[2])
    batch_data['batch_size'] = batch_size
    return batch_data


def collate_fn_dense_full(batch, num_partitions):
    """
        Combine each sample in a batch
        For dense features
    """
    batch_data = {}
    batch_size = len(batch)
    emb_dims = batch[0][0].size
    batch_data['X'] = np.zeros((batch_size, emb_dims))
    for idx, _batch in enumerate(batch):
        batch_data['X'][idx, :] = _batch[0]
    batch_data['X'] = torch.from_numpy(batch_data['X']).type(torch.FloatTensor)
    batch_data['Y'] = torch.stack([torch.from_numpy(x[1]) for x in batch], 0)
    batch_data['batch_size'] = batch_size
    return batch_data


def collate_fn_sparse_full(batch, num_partitions):
    """
        Combine each sample in a batch
        For sparse features
    """
    _is_partitioned = True if num_partitions > 1 else False
    batch_data = {}
    batch_size = len(batch)
    seq_lengths = [len(item[0][0]) for item in batch]
    batch_data['X'] = torch.zeros(batch_size, max(seq_lengths)).long()
    batch_data['X_w'] = torch.zeros(batch_size, max(seq_lengths))
    sequences = [item[0] for item in batch]
    for idx, (seq, seqlen) in enumerate(zip(sequences, seq_lengths)):
        batch_data['X'][idx, :seqlen] = torch.LongTensor(seq[0])
        batch_data['X_w'][idx, :seqlen] = torch.FloatTensor(seq[1])
    batch_data['Y'] = torch.stack([torch.from_numpy(x[1]) for x in batch], 0)
    batch_data['batch_size'] = batch_size
    return batch_data
