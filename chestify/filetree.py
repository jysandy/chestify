class FileTree:
    """ Represents the user's filesystem as a nested dict structure.
    """
    
    def __init__(self):
        self.fs = { 'folders' : dict(), 'files' : dict() }
        
        
    def add_path(self, path, meta={}):
        """ Adds a complete file path to the filesystem.
            Empty directories are represented as '.dir' files.
            Ex: /home/sandy/.dir represents the empty directory /home/sandy.
        """
        parts = path.split('/')
        path_list = parts[:-1]
        file = parts[-1]
        pwd = self.fs
        while len(path_list) > 0 and path_list[0] in pwd['folders']:
            #Walk the filesystem
            pwd = pwd['folders'][path_list[0]]
            path_list = path_list[1:]
        while len(path_list) > 0:
            #Create the needed subfolders
            pwd['folders'][path_list[0]] = { 'folders' : dict(), 'files' : dict() }
            pwd = pwd['folders'][path_list[0]]
            path_list = path_list[1:]
        if file != '.dir':
            #Finally add the file
            pwd['files'][file] = meta