# Python 2/3 compatibility
from __future__ import print_function
import os, re, sys, time
import numpy as np
from colorama import Fore

def tstack(a):
    """
    Stacks arrays in sequence along the last axis (tail).
    Rebuilds arrays divided by :func:`tsplit`.
    Parameters
    ----------
    a : array_like
        Array to perform the stacking.
    Returns
    -------
    ndarray
    See Also
    --------
    tsplit
    Examples
    --------
    >>> a = 0
    >>> tstack((a, a, a))
    array([0, 0, 0])
    >>> a = np.arange(0, 6)
    >>> tstack((a, a, a))
    array([[0, 0, 0],
           [1, 1, 1],
           [2, 2, 2],
           [3, 3, 3],
           [4, 4, 4],
           [5, 5, 5]])
    >>> a = np.reshape(a, (1, 6))
    >>> tstack((a, a, a))
    array([[[0, 0, 0],
            [1, 1, 1],
            [2, 2, 2],
            [3, 3, 3],
            [4, 4, 4],
            [5, 5, 5]]])
    >>> a = np.reshape(a, (1, 1, 6))
    >>> tstack((a, a, a))
    array([[[[0, 0, 0],
             [1, 1, 1],
             [2, 2, 2],
             [3, 3, 3],
             [4, 4, 4],
             [5, 5, 5]]]])
    """
    a = np.asarray(a)

    return np.concatenate([x[..., np.newaxis] for x in a], axis=-1)

def tsplit(a):
    """
    Splits arrays in sequence along the last axis (tail).
    Parameters
    ----------
    a : array_like
        Array to perform the splitting.
    Returns
    -------
    ndarray
    See Also
    --------
    tstack
    Examples
    --------
    >>> a = np.array([0, 0, 0])
    >>> tsplit(a)
    array([0, 0, 0])
    >>> a = np.array([[0, 0, 0],
    ...               [1, 1, 1],
    ...               [2, 2, 2],
    ...               [3, 3, 3],
    ...               [4, 4, 4],
    ...               [5, 5, 5]])
    >>> tsplit(a)
    array([[0, 1, 2, 3, 4, 5],
           [0, 1, 2, 3, 4, 5],
           [0, 1, 2, 3, 4, 5]])
    >>> a = np.array([[[0, 0, 0],
    ...                [1, 1, 1],
    ...                [2, 2, 2],
    ...                [3, 3, 3],
    ...                [4, 4, 4],
    ...                [5, 5, 5]]])
    >>> tsplit(a)
    array([[[0, 1, 2, 3, 4, 5]],
    <BLANKLINE>
           [[0, 1, 2, 3, 4, 5]],
    <BLANKLINE>
           [[0, 1, 2, 3, 4, 5]]])
    """
    a = np.asarray(a)

    return np.array([a[..., x] for x in range(a.shape[-1])])

def filter_files(directory, extensions):
    """
    Filters given directory for files matching given extensions.

    Parameters
    ----------
    directory : unicode
        Directory to filter.
    extensions : tuple or list
        Extensions to filter on.

    Returns
    -------
    list
        Filtered files.
    """

    return map(lambda x: os.path.join(directory, x),
               filter(lambda x: re.search('{0}$'.format(
                   '|'.join(extensions)), x), sorted(os.listdir(directory))))

class ProgressBar(object):
    '''
    progress = ProgressBar(80, fmt=ProgressBar.FULL)

    for x in xrange(progress.total):
        progress.current += 1
        progress()
        sleep(0.1)
    progress.done()
    '''
    DEFAULT = 'Progress: %(bar)s %(percent)3d%%'
    FULL = '%(bar)s %(current)d/%(total)d (%(percent)3d%%) %(remaining)d to go'

    def __init__(self, total, width=40, fmt=DEFAULT, symbol='=',
                 output=sys.stderr):
        assert len(symbol) == 1

        self.total = total
        self.width = width
        self.symbol = symbol
        self.output = output
        self.fmt = re.sub(r'(?P<name>%\(.+?\))d',
            r'\g<name>%dd' % len(str(total)), fmt)

        self.current = 0

    def __call__(self):
        percent = self.current / float(self.total)
        size = int(self.width * percent)
        remaining = self.total - self.current
        bar = '[' + self.symbol * size + ' ' * (self.width - size) + ']'

        args = {
            'total': self.total,
            'bar': bar,
            'current': self.current,
            'percent': percent * 100,
            'remaining': remaining
        }
        print('\r' + self.fmt % args, file=self.output, end='')

    def done(self):
        self.current = self.total
        self()
        print('', file=self.output)

def imgBrighten(img, pBrightest):

    Ibrightest = np.percentile(img.flatten(), pBrightest, interpolation='midpoint')

    img2 = np.minimum(np.nan_to_num(img/Ibrightest), 1)

    return img

def get_time_hhmmss(start):

    end = time.time()
    m, s = divmod(end - start, 60)
    h, m = divmod(m, 60)
    time_str = "%02d:%02d:%02d" % (h, m, s)
    return time_str