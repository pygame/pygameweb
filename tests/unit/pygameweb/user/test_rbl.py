


def test_rbl():
    """ handles failure ok, and handles lookups ok with dns module.
    """
    import mock
    from dns.resolver import NoAnswer, NXDOMAIN, NoNameservers

    from pygameweb.user.rbl import rbl

    assert rbl('127.0.0.1') is False
    assert rbl('') is False

    with mock.patch('dns.resolver.query') as query:
        query.side_effect = NoAnswer()
        assert rbl('192.168.0.1') is False
        query.side_effect = NXDOMAIN()
        assert rbl('192.168.0.1') is False
        query.side_effect = NoNameservers()
        assert rbl('192.168.0.1') is False

    with mock.patch('dns.resolver.query') as query:
        query.side_effect = '127.0.0.2'
        assert rbl('192.168.0.1') is True
        assert query.called
