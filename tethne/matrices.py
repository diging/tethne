import numpy as np
import uuid, sys
from tethne.data import get_hdf5_matrix
from scipy.sparse import coo_matrix



def cooccurrence(featureset, matrix_backend=None, hdf5_repo=None, hdf5_matrix_name=None):
    data, docs, vocab = featureset.transform(lambda *a: 1 if a[1] > 0 else 0).to_coo_matrix()
    data_c = data.tocsc()    # Slice on columns.

    N_d, N_f = data.shape
    block = min(2054, N_f)

    if matrix_backend == 'hdf5':
        hdf5_matrix_name = hdf5_matrix_name if hdf5_matrix_name else 'cooccurrence'
        out = get_hdf5_matrix(hdf5_repo, hdf5_matrix_name, 'float64', (N_f, N_f), chunkshape=(block, block))
    else:
        out = np.zeros((N_f, N_f), dtype='float64')

    # Since we only care about the upper triangle, we'll start each chunk on
    #  the diagonal. Part of the first chunk in each row will bleed over, but
    #  that doesn't matter so long as subsequent analysis focuses on the upper
    #  triangle only.
    for i in xrange(0, N_f, block):
        for j in xrange(i, N_f, block):
            print '\r', i, j,
            sys.stdout.flush()
            out[i:min(i+block, N_f), j:min(j+block, N_f)] = (data_c[:, i:min(i+block, N_f)].T.dot(data_c[:, j:min(j+block, N_f)])).todense()
    return out, docs, vocab


def pointwise_mutual_information(featureset, matrix_backend=None,
                                 hdf5_repo=None, hdf5_matrix_name=None,
                                 min_weight=0.999):
    hdf5_matrix_name = hdf5_matrix_name if hdf5_matrix_name else 'cooccurrence'
    data, docs, vocab = cooccurrence(featureset, matrix_backend, hdf5_repo, hdf5_matrix_name)
    N_d = len(docs)
    N_f = data.shape[0]
    block = min(2054, N_f)

    if matrix_backend == 'hdf5':
        name = hdf5_matrix_name + '_npmi'
        dtype = 'float64'
        shape = (N_f, N_f)
        out_full = get_hdf5_matrix(hdf5_repo, name, dtype, shape,
                                   chunkshape=(block, block))
    else:
        out_full = np.zeros((N_f, N_f), dtype='float64')

    out_sparse = []

    # Building this ahead of time is costly. We don't have enough memory to
    #  load the whole cooccurrence matrix at once, and iterating over the
    #  compressed array just to pull out the diagonal would be super
    #  inefficient. So we will build it as we go, below. The does limit
    #  parallelization slightly (see below), but probably worth it.
    freq = np.zeros((N_f), )

    for i in xrange(0, N_f, block):
        for j in xrange(i, N_f, block):
            print '\r', i, j,
            sys.stdout.flush()
            selection = data[i:min(i + block, N_f), j:min(j + block, N_f)]

            # We are progressively extending the diagonal values from the
            #  co-occurrence matrix. If we parallelize this later on, we will
            #  have to group together tasks that depend on this section of the
            #  diagonal.
            if i == j:  # This chunk sits on the diagonal.
                freq[i:min(i + block, N_f)] = selection.diagonal() / N_d

            # The observed frequency of two terms occurring together.
            p_xy = selection / N_d
            p_xy = np.ma.MaskedArray(p_xy, p_xy == 0, fill_value=0.0)

            # Calculate the probability of two terms occurring together by
            #  chance alone.
            p_x = freq[i:min(i + block, N_f)]
            p_y = freq[j:min(j + block, N_f)]
            p_x__p_y = p_x.reshape(p_x.shape[0], 1) * p_y.reshape(p_y.shape[0], 1).T

            ## Calculate PMI. ##
            chunk = p_xy / (p_x__p_y)    # The inner ratio.
            chunk = np.log(chunk)    # This still throws RuntimeWarning.

            ## Calculated nPMI. ##
            lower = -1. * np.log(p_xy)
            chunk = chunk / lower

            # This should apply the last fill value.
            chunk = chunk.filled()

            # There is something fishy going on here, where we are getting
            #  spurious values > 1. Everything else seems to be in order, so
            #  we'll clobber these for now. But TODO: we should investigate
            #  what is causing this.
            chunk[np.where(chunk > 1.0)] = 0.

            # Store the chunk.
            out_full[i:min(i + block, N_f), j:min(j + block, N_f)] = chunk

            # Look for cells that meet the search criteria (e.g. for a graph
            #  representation).
            for x, y in zip(*np.where(chunk >= min_weight)):
                if j+y > i+x:   # We only care about the upper triangle.
                    out_sparse.append((i+x, j+y, chunk[x, y]))

    # Just pass back the bits of the graph with values above the indicated
    #  threshold.
    return out_sparse, docs, vocab
