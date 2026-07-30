from src.utils.text_parser import parser


def test_parser():
    assert parser('!!!gly') == 'gly'