import unittest

from pyramid import testing


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
    

class ViewTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()
