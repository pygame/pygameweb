""" Reverse black list lookups, to try and prevent spam.

Using dns, we can check if their ip address is listed on some spam lists.

http://www.dnspython.org/
https://en.wikipedia.org/wiki/DNSBL
http://whatismyipaddress.com/blacklist-check
https://en.wikipedia.org/wiki/Comparison_of_DNS_blacklists

"""
import dns.resolver
from dns.reversename import from_address


def rbl(ip_address):
    """ Returns true if the ip_address is in a rbl.
    """
    if not ip_address or ip_address == '127.0.0.1':
        return False
    lists = ['all.s5h.net', 'cbl.abuseat.org']
    return [l for l in lists if rbl_list(ip_address, l)] != []


def rbl_list(address, black_list):
    """ Returns True if the list is in an rbl given at black_list.
    """
    reversed_ip = from_address(address)
    domain = str(reversed_ip.split(3)[0]) + '.' + black_list
    try:
        dns.resolver.query(domain, 'a')
    except (dns.resolver.NXDOMAIN,
            dns.resolver.NoNameservers,
            dns.resolver.NoAnswer):
        return False
    return True
