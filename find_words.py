# -*- coding: UTF-8 -*-
import codecs
import os
import re

class FindWords(object):
    def __init__(self, input_dir, output_dir, extension=".php"):
        '''
        input_dir: 查找的目录
        output_dir: 输出的目录，建议空目录
        extension：查找的文件的后缀
        '''
        self.input_dir = os.path.abspath(input_dir)
        output_dir = os.path.abspath(output_dir)
        not os.path.exists(output_dir) and os.mkdir(output_dir)
        self.output_dir = output_dir
        self.inoutfiles = list()
        self.extension = extension
        self.result_cache_path = self._get_output_file("words_cache")
        self.cache_files_path = self._get_output_file("files_cache")

    def run(self):
        self.find_file_names()
        self.find_words()
        self.count_words()

    def find_file_names(self):
        print_step = 1000
        if not os.path.exists(self.cache_files_path) or os.path.getsize(self.cache_files_path) < 10:
            for root, dirs, files in os.walk(self.input_dir):
                for thefile in files:
                    if thefile.endswith(self.extension):
                        path = os.path.join(root, thefile)
                        if not (
                            os.path.getsize(path) > 10
                            and os.path.getsize(path) < 1000000
                        ):
                            continue
                        self.inoutfiles.append(path)
                        len(self.inoutfiles)%print_step or print("\r%d files were found." % len(self.inoutfiles)*print_step, end="")
            print('\nFind files.')
            self._write_list(self.cache_files_path, self.inoutfiles)
        else:
            print('Read files cache.')
            stream = codecs.open(self.cache_files_path, "r")
            for line in stream:
                self.inoutfiles.append(line.strip())

    def find_words(self):
        if not os.path.exists(self.result_cache_path) or os.path.getsize(self.result_cache_path) < 10:
            print('Find words form files.')
            print("Total number: %d" % len(self.inoutfiles))

            reg = re.compile(r"[_\-\s]?([A-Z][a-z]+|[a-z]+|[A-Z]+)[_\-\s]?")
            for index in range(len(self.inoutfiles)):
                index % 100 or print("\r%s"%str(index), end="")
                result = dict()
                try:
                    content = codecs.open(self.inoutfiles[index], "r", "utf-8").read()
                except Exception as e:
                    print("\n    error file:")
                    print("               ",end='')
                    print(self.inoutfiles[index])
                    print("               ",end='')
                    print(e)
                    continue
                for v in reg.findall(content):
                    result[v] = result.get(v, 0) + 1
                codecs.open(self.result_cache_path, "a+").write(
                    "".join(["%s,%d\n" % x for x in result.items()])
                )
            print("\rok: %d" % len(self.inoutfiles))
        else:
            print('Read works cache.')

    def count_words(self):
        words_dict = dict()
        with codecs.open(self.result_cache_path, "r") as data_file:
            for line in data_file:
                name, num = line.strip().split(",")
                name = name.lower()
                words_dict[name] = words_dict.get(name, 0) + int(num)
        print('Save words.')
        self._write_list(
            self._get_output_file("words.csv"),
            sorted(words_dict.items(), key=lambda params: params[1], reverse=True),
            lambda params: "%s,%d" % params,
        )

    def _get_output_file(self, fileNames):
        return os.path.join(self.output_dir, fileNames)

    def _write_list(self, output_path, output_list, format=lambda item: item):
        print("Total number: %d" % len(output_list))
        cacheStream = codecs.open(output_path, "a+")
        list_group = list()
        list_step = min(int(len(output_list)/100), 100)
        for l in range(0, len(output_list), list_step):
            list_group.append(output_list[l : l + list_step])
        for i in range(len(list_group)):
            print("\r%d" % (i * list_step), end="")
            thestr = "".join([format(x) + "\n" for x in list_group[i]])
            cacheStream.write(thestr)
        print("\rok: %d" % len(output_list))
        cacheStream.close()
