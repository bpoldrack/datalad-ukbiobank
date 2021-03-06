from datalad.api import (
    create,
    ukb_init,
)
from datalad.tests.utils import (
    assert_not_in,
    assert_status,
    eq_,
    with_tempfile,
)


@with_tempfile
def test_base(path):
    ds = create(path)
    ds.ukb_init('12345', ['20249_2_0', '20249_3_0', '20250_2_0'])
    # standard branch setup
    eq_(sorted(ds.repo.get_branches()),
        ['git-annex', 'incoming', 'incoming-native', 'master'])
    # standard batch file setup
    eq_(ds.repo.call_git(['cat-file', '-p', 'incoming:.ukbbatch']),
        '12345 20249_2_0\n12345 20249_3_0\n12345 20250_2_0\n')
    # intermediate branch is empty
    eq_(ds.repo.call_git(['ls-tree', 'incoming-native']), '')
    # no batch in master
    assert_not_in('ukbbatch', ds.repo.call_git(['ls-tree', 'master']))

    # no re-init without force
    assert_status(
        'error',
        ds.ukb_init('12', ['12', '23'], on_failure='ignore'))

    ds.ukb_init('12345', ['20250_2_0'], force=True)
    eq_(ds.repo.call_git(['cat-file', '-p', 'incoming:.ukbbatch']),
        '12345 20250_2_0\n')


@with_tempfile
def test_bids(path):
    ds = create(path)
    ds.ukb_init('12345', ['20249_2_0', '20249_3_0', '20250_2_0'],
                bids=True)
    # standard branch setup
    eq_(sorted(ds.repo.get_branches()),
        ['git-annex', 'incoming', 'incoming-bids', 'incoming-native',
         'master'])
    # intermediate branches are empty
    for b in 'incoming-bids', 'incoming-native':
        eq_(ds.repo.call_git(['ls-tree', b]), '')
    # no batch in master
    assert_not_in('ukbbatch', ds.repo.call_git(['ls-tree', 'master']))

    # smoke test for a reinit
    ds.ukb_init('12345', ['20250_2_0'], bids=True, force=True)
    eq_(sorted(ds.repo.get_branches()),
        ['git-annex', 'incoming', 'incoming-bids', 'incoming-native',
         'master'])
