
def create_faux_file_system():
    return Cursor(FFSDirectory())

class FFSError(Exception):
    def __init__(self, error):
        super(Exception, self).__init__(error)

class Cursor(object):
    def __init__(self, root, start='/'):
        self.root = root
        self.cwd = root
        self.wd_text = []

        if self.root.is_file:
            raise FFSError('Must create cursor on directory node')

        self.cd(start)

    def mkdir(self, name):
        self.cwd.set_child(name, FFSDirectory())

    def open(self, name, create=False):
        if not name in self.cwd.children:
            if create:
                self.cwd.set_child(name, FFSFile(b''))
            else:
                raise FFSError(f'File [{name}] does not exist in [{self}]')
        return FFSFileHandle(self.cwd.children[name])

    def cd(self, path):
        elements = path.rstrip('/').split('/')
        print(elements)
        if elements[0] == '':
            self.cwd = self.root
            self.wd_text = []
            elements = elements[1:]

        for element in elements:
            # Identity
            if element == '.':
                continue
            # Level up
            elif element == '..':
                if self.cwd == self.root:
                    raise FFSError('Cannot traverse above cursor root')
                self.cwd = self.cwd.parent
                self.wd_text = self.wd_text[:-1]
            else:
                new_wd = self.cwd.children.get(element)
                if new_wd is None:
                    raise FFSError(f'No node [{element}] in [{self}]')
                elif new_wd.is_file:
                    raise FFSError(f'Cannot traverse into file node [{self}{element}]')
                else:
                    self.cwd = new_wd
                    self.wd_text.append(element)

    def ls(self):
        return [(k, 'file' if self.cwd.children[k].is_file else 'directory') for k in self.cwd.children.keys()]

    def __str__(self):
        return '/' + '/'.join(self.wd_text)

class FFSFileHandle(object):
    def __init__(self, file):
        if not file.is_file:
            raise FFSError(f'Handle must be opened on file, not directory')
        self.file = file

    def write(self, data):
        if self.file.read_only:
            raise FFSError('Cannot write to readonly file')

        self.file.data += data

class FFSFile(object):
    def __init__(self, data, read_only=False):
        self.data = data
        self.read_only = read_only
        self.is_file = True
        self.parent = None

    def get_data(self):
        return self.data

    def set_data(self, data):
        if self.read_only:
            raise FFSError('Attempted to change readonly object')
        self.data = data

class FFSDirectory(object):
    def __init__(self):
        self.children = {}
        self.is_file = False
        self.parent = None

    def set_child(self, name, node, force=False):
        if name in self.children and not force:
            raise FFSError('Attempting to overwrite node [{name}], use "force=True" if intentional')

        self.children[name] = node
        node.parent = self





