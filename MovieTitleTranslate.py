#!/usr/bin/python
# -*- coding: UTF-8 -*-

import xml.etree.ElementTree as ET
import sys, os


startDir = sys.argv[1]
print(startDir)
movies = os.listdir(startDir)
for m in movies:
  title = ''
  year = ''
  mPath = startDir + '/' + m
  print('==========================')
  print('begin to rename:',m)
  try:
    for home, dirs, files in os.walk(mPath):
      for fName in files:
        if fName.endswith('nfo'):
          fPath = mPath + '/' + fName
          nfoTree = ET.parse(fPath)
          nfoRoot = nfoTree.getroot()
          title = nfoRoot.find('title').text
          year = nfoRoot.find('year').text
          break
      break
    newMPath = startDir + '/' + title + '('+ year+')'
    print(newMPath)
    os.rename(mPath, newMPath)
  except:
    print("rename <%s> failed!..." % m)
    print('==========================')
    continue
  print('rename successfully!!!!!!!!')
  print('==========================')



    
        
