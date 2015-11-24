import unittest
from unittest.mock import Mock
import transaction
from pyramid import testing
from .models import User, Link
from .mocks import ObjectMock
from copy import deepcopy


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
        bucket_mock = Mock()
        bucket_mock.objects = Mock()
        bucket_mock.objects.all = Mock(return_value=[
            ObjectMock(key='sandy/home/foo/goo.txt'),
            ObjectMock(key='sandy/home/goo/.dir'),
            ObjectMock(key='bhas/work/baz.dat')
        ])
        self.s3_mock = Mock()
        self.s3_mock.Bucket = Mock(return_value=bucket_mock)
        self.s3_mock.Object = Mock(return_value=ObjectMock())
        import boto3
        self.prev_boto3_resource = deepcopy(boto3.resource)
        boto3.resource = Mock(return_value=self.s3_mock)

    def tearDown(self):
        import boto3
        self.session.remove()
        testing.tearDown()
        boto3.resource = self.prev_boto3_resource

    def test_list_files(self):
        from .views import list_files
        from .filetree import FileTree
        self.config.testing_securitypolicy(userid='sandy')
        request = testing.DummyRequest()
        response = list_files(request)
        expected = FileTree()
        expected.add_path('home/foo/goo.txt', {'size': 0, 'last_modified': 'Dec 21 2012'})
        expected.add_path('home/goo/.dir', {'size': 0, 'last_modified': 'Dec 21 2012'})
        self.assertEqual(expected.fs, response)
        user = self.session.query(User).filter(User.uid == 'sandy').one()
        self.assertEqual(0, user.data_used)

    def test_download_url(self):
        from .views import download_url
        self.config.testing_securitypolicy(userid='sandy')
        request = testing.DummyRequest()
        request.params['key'] = 'home/foo/goo.txt'
        response = download_url(request)
        self.assertTrue(response['url'].startswith('https'))

    def test_upload_url(self):
        from .views import upload_url
        self.config.testing_securitypolicy(userid='sandy')
        request = testing.DummyRequest()
        request.params['key'] = 'home/foo/goo.virus'
        request.params['file_size'] = 400
        response = upload_url(request)
        self.assertTrue(response['url'].startswith('https'))

    def test_create_directory(self):
        from chestify.views import create_directory
        self.config.testing_securitypolicy(userid='sandy')
        request = testing.DummyRequest()
        request.params['key'] = 'home/foo/goo'
        response = create_directory(request)
        self.assertEqual({'result': 'success'}, response)

    def test_shared_download(self):
        from .views import shared_download
        from pyramid.httpexceptions import HTTPFound
        link = Link(key='sandy/home/bar/foobar.txt')
        self.session.add(link)
        self.session.flush()
        self.session.refresh(link)
        request = testing.DummyRequest()
        request.params['id'] = link.uid
        response = shared_download(request)
        self.assertEqual(HTTPFound, type(response))
        self.assertTrue(response.location.startswith('https'))

    def test_generate_shared(self):
        from .views import generate_shared
        self.config.testing_securitypolicy(userid='sandy')
        request = testing.DummyRequest()
        request.params['key'] = 'home/foo/goo.txt'
        response = generate_shared(request)
        self.assertNotEqual(None, response['link_id'])
        link = self.session.query(Link).filter(Link.uid == response['link_id']).one()
        self.assertEqual(link.key, 'sandy'+'/'+request.params['key'])

    def test_not_logged_in(self):
        from pyramid.httpexceptions import HTTPForbidden
        from .views import list_files, download_url, upload_url
        request = testing.DummyRequest()
        response = list_files(request)
        self.assertEqual(HTTPForbidden, type(response))
        request.params['key'] = 'home/foo/goo.txt'
        response = download_url(request)
        self.assertEqual(HTTPForbidden, type(response))
        response = upload_url(request)
        self.assertEqual(HTTPForbidden, type(response))
