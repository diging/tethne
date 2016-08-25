import tables as tb
import uuid

_dtypes = {
    'int32': tb.Int32Atom,
    'float64': tb.Float64Atom,
}


def get_hdf5_matrix(hdf5_repo, hdf5_matrix_name, dtype, shape, chunkshape):
    """

    """
    if hdf5_repo is None:
        hdf5_repo = tb.open_file('%s.h5' % str(uuid.uuid4()), 'w')
    elif type(hdf5_repo) in [str, unicode]:    # Path to a repo.
        hdf5_repo = tb.open_file(hdf5_repo, 'w')    # Get or create.

    filters = tb.Filters(complevel=5, complib='blosc')
    return hdf5_repo.create_carray(hdf5_repo.root, hdf5_matrix_name,
                                   _dtypes[dtype](), shape=shape,
                                   filters=filters, chunkshape=chunkshape)
