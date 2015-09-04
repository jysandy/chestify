class FileTree:
    def __init__(self):
        self.fs = { 'folders' : dict(), 'files' : dict() }
        
        
    def add_path(self, path):
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
            pwd['files'][file] = dict()