import sublime
import sublime_plugin
import os
import functools
import re
import xml.etree.ElementTree
import sublime, sublime_plugin

#for bolt, switch between *.xml.lua and *.xml
class XmlToLua(sublime_plugin.TextCommand):
    def run(self,edit):
        #print('abc')
        if self.view.file_name() == None:
            return
        else:
            filename, file_extension = os.path.splitext(self.view.file_name())
            window = sublime.active_window()
            if file_extension == ".xml":
                window.open_file(filename+".xml.lua")
            elif file_extension == ".lua":
                if os.path.isfile(filename) :
                    window.open_file(filename)
                else:
                    pass

class FileWrapper:
    def __init__(self, source):
        self.source = source
        self.lineno = 0
    def read(self, bytes):
        s = self.source.readline()
        self.lineno += 1
        return s

def get_filepaths(directory):
    """
    This function will generate the file names in a directory 
    tree by walking the tree either top-down or bottom-up. For each 
    directory in the tree rooted at directory top (including top itself), 
    it yields a 3-tuple (dirpath, dirnames, filenames).
    """
    file_paths = []  # List which will store all of the full filepaths.

    # Walk the tree.
    for root, directories, files in os.walk(directory):
        for filename in files:
            # Join the two strings in order to form the full filepath.
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)  # Add it to the list.

    return file_paths  # Self-explanatory.

class GoDefinition(sublime_plugin.TextCommand):
    def run(self,edit):
        if self.view.file_name() == None:
            return
        else:
            # select or not
            rg = self.view.sel()[0]
            select_world = None
            if rg.a == rg.b:
                row, col = self.view.rowcol(rg.a)
                row = row + 1
                xml_line = self.view.substr(self.view.line(self.view.sel()[0].a))
                p = re.compile('\"([^"]*)\"')                
                for m in p.finditer(xml_line):
                    if col >= m.start()+1 and col <= m.end()-1:
                        select_world = xml_line[m.start()+1:m.end()-1]
                if select_world is None:
                    p = re.compile('\'([^"]*)\'')                
                    for m in p.finditer(xml_line):
                        if col >= m.start()+1 and col <= m.end()-1:
                            select_world = xml_line[m.start()+1:m.end()-1]
                    if select_world is None:
                        p = re.compile('(>(.*)</)')
                        for m in p.finditer(xml_line):
                            found = xml_line[m.start()+1:m.end()-2]
                            while found is not None:
                                select_world = found
                                found = None
                                for m in p.finditer(select_world):
                                    found = select_world[m.start()+1:m.end()-2]
            else:
                select_world = self.view.substr(rg)
            if select_world is None:
                return
            #filename, file_extension = os.path.splitext(self.view.file_name())
            window = sublime.active_window()
            project_data = window.project_data()
            #print(project_data)
            for folders in project_data['folders']:
                full_file_paths = get_filepaths(folders['path'])
                for filename in full_file_paths:
                    if filename.endswith(".xml"):
                        # print(f)
                        openf = open(filename,encoding="utf-8")
                        try:
                            f = FileWrapper(openf)
                            for event, elem in xml.etree.ElementTree.iterparse(f,("start","end")):
                                #print("iterparse")
                                #if event == "start":
                                #print(f.lineno, event, elem, elem.get('class'))
                                if event == 'start' and ((elem.tag == 'control' and elem.get('class') == select_world) or (elem.tag == 'objtemplate' and elem.get('id') == select_world) or (elem.tag == 'bitmap' and elem.get('id') == select_world) or (elem.tag == 'texture' and elem.get('id') == select_world) or (elem.tag == 'imagelist' and elem.get('id') == select_world) or (elem.tag == 'color' and elem.get('id') == select_world) or (elem.tag == 'font' and elem.get('id') == select_world) or (elem.tag == 'pen' and elem.get('id') == select_world) or (elem.tag == 'hostwndtemplate' and elem.get('id') == select_world) or (elem.tag == 'objtreetemplate' and elem.get('id') == select_world) or (elem.tag == 'texture' and elem.get('id') == select_world)  or (elem.tag == 'gif' and elem.get('id') == select_world)):
                                     #print(f.lineno, event, elem, elem.get('class'))
                                     window.open_file("%s:%d:%d" % (filename, f.lineno, 0), sublime.ENCODED_POSITION)
                        finally:
                            openf.close()