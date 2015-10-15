import unittest
import transaction
from pyramid import testing
from .models import User, Link


class FileTreeTests(unittest.TestCase):
    def test_file_tree_2(self):
        from .filetree import FileTree
        ft = FileTree()
        file_list = [
            'home/bhas/goo.txt',
            'home/sandy/bar.txt'
        ]
        for path in file_list:
            ft.add_path(path)
        expected = {
            'folders': {
                'home': {
                    'folders': {
                        'bhas': {
                            'folders': dict(),
                            'files': {
                                'goo.txt': dict()
                            }
                        },
                        'sandy': {
                            'folders': dict(),
                            'files': {
                                'bar.txt': dict()
                            }
                        }
                    },
                    'files': dict()
                }
            },
            'files': dict()
        }
        self.assertEqual(ft.fs, expected)

    def test_file_tree3(self):
        from .filetree import FileTree
        ft = FileTree()
        file_list = [
            'home/bhas/goo.txt',
            'home/sandy/.dir',
            'home/sandy/bar.txt',
            'home/sandy/.dir'
        ]
        for path in file_list:
            ft.add_path(path)
        expected = {
            'folders': {
                'home': {
                    'folders': {
                        'bhas': {
                            'folders': dict(),
                            'files': {
                                'goo.txt': dict()
                            }
                        },
                        'sandy': {
                            'folders': dict(),
                            'files': {
                                'bar.txt': dict()
                            }
                        }
                    },
                    'files': dict()
                }
            },
            'files': dict()
        }
        self.assertEqual(ft.fs, expected)

    def test_file_tree(self):
        from .filetree import FileTree
        ft = FileTree()
        file_list = [
            'home/bhas/goo.txt',
            'home/sandy/bar.txt',
            'home/sandy/hue/.dir'
        ]
        for path in file_list:
            ft.add_path(path)
        expected = {
            'folders': {
                'home': {
                    'folders': {
                        'bhas': {
                            'folders': dict(),
                            'files': {
                                'goo.txt': dict()
                            }
                        },
                        'sandy': {
                            'folders': {
                                'hue': {
                                    'folders': dict(),
                                    'files': dict()
                                }
                            },
                            'files': {
                                'bar.txt': dict()
                            }
                        }
                    },
                    'files': dict()
                }
            },
            'files': dict()
        }
        self.assertEqual(ft.fs, expected)
    

def _init_testing_db():
    from sqlalchemy import create_engine
    from .models import (
        DBSession,
        User,
        Link,
        Base
    )
    engine = create_engine('sqlite://')
    Base.metadata.create_all(engine)
    DBSession.configure(bind=engine)
    with transaction.manager:
        user = User(uid='sandy', email='uhuhu@gmail.com', data_used=15)
        DBSession.add(user)
    return DBSession


class ViewTests(unittest.TestCase):
    def setUp(self):
        self.session = _init_testing_db()
        self.config = testing.setUp()

    def tearDown(self):
        self.session.remove()
        testing.tearDown()

    def test_list_files(self):
        from .views import list_files
        from .filetree import FileTree
        self.config.testing_securitypolicy(userid='sandy')
        request = testing.DummyRequest()
        response = list_files(request)
        self.assertEqual(FileTree().fs, response)
        user = self.session.query(User).filter(User.uid == 'sandy').one()
        self.assertEqual(0, user.data_used)

    def test_download_url(self):
        from .views import download_url
        self.config.testing_securitypolicy(userid='sandy')
        request = testing.DummyRequest()
        request.params['key'] = 'home/foo/goo.txt'
        response = download_url(request)
        self.assertTrue(response['url'].startswith('https'))
