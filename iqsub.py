#!/usr/bin/python


#import shutil
import os,sys
import itertools
#from copy import copy

def print_usage():
  print('\n wrong number of input parameter.\n\nexample of usage:\n$ ./iqsub.py iqsubmit.dat\n\n')
  exit()

def ReadFile(fileName):
   f = open(fileName, 'r')
   file1 = f.readlines()
   f.close
   
   file2 = []
   for lines in file1:
      file2.append(lines.strip())
   return file2
   
def findParameterLine(parameterName,fileList):
   parameterFound = False
   for index in range(0,len(fileList)):
      line = fileList[index]
      if len(line) > len(parameterName):
         if line[:len(parameterName)]==parameterName:
            parameterFound = True
            break
   if parameterFound:
     return line
   else:
     return ''


input_string_list = sys.argv[:]

if(len(input_string_list)!=2): 
  print_usage()


#print(input_string_list)
fileList = ReadFile(sys.argv[1])


def ReadRange(inputStr):
  range1 = inputStr.split(':')
  numberList = []
  if(len(range1)!=1):
    assert(len(range1)==3)
    start = float(range1[0])
    incr = float(range1[1])
    end = float(range1[2])
    value = start
    if(incr>0):
      assert(start<end)
      while(value<=end):
        numberList.append(value)
        value+=incr
        value=round(value*10000000.)/10000000.  #to clean float errors
    else:
      assert(start>end)
      while(value>=end):
        numberList.append(value)
        value+=incr
        value=round(value*10000000.)/10000000.  #to clean float errors
  else:
    numberList = [float(range1[0])]
  return numberList


#inputStr = '2:0.1:10'
#print ReadRange(inputStr)
#print ReadRange('2.0')
#exit()


paramNames1=[]
paramNames2=[]

paramValuesList1=[]
paramValuesList2=[]
for i in range(1,100):  # must have less than 100 parameters
  param = findParameterLine('param'+str(i),fileList)
  if param != '':
    paramLineList = param.split('=')
    paramNameCoupled = paramLineList[1].strip(' \t\n()')
    
    paramName=paramNameCoupled.split(',')
    paramNames1.append(paramName)
    for name in paramName:
      if(name in paramNames2):
        print('error: the parameter name %s is used more than once.\n'%name)
        exit()
      paramNames2.append(name)
    
    paraValue = []
    for k in range(len(paramName)):
      paraValue.append([])
    
    if(len(paramName)>1):
      
      #print('coupledParameters')
      paramValues = paramLineList[2].strip(' \t\n[]').replace('(','--').replace(')','--').split('--')
      #print paramValues
      for j in range(len(paramValues)):
        if(j%2==1):
          paramValueCouple = paramValues[j].split(',')
          if(len(paramValueCouple)!=len(paramName)):
            print('error: cannot read the %.\n'%('param'+str(i)) )
            exit()
      
          for k in range(len(paramName)):
            paraValue[k].extend(ReadRange(paramValueCouple[k]))
      testLen = len(paraValue[0])
      for k in range(len(paramName)):
        if(testLen != len(paraValue[k]) ):
          print('error: coupled parameters in %s have different dimension, due to a wrong definition.\n'%('param'+str(i)) )
          exit()
    else:
      #print 'simpleParameter'
      paramValues = paramLineList[2].strip(' \t\n[]').replace(',',' ').split()
      for j in range(len(paramValues)):
        paraValue[0].extend(ReadRange(paramValues[j]))
      
    paramValuesList1.append(paraValue)
      
  else:
    break



paramValuesDistribution = [None]*len(paramNames2)

#exit()

#totalNbOfParamDistribution=1
#nbOfValuesPerParam=[]
combinedCouplesListOfList = []
for i in range(len(paramValuesList1)):
  length_of_list = len(paramValuesList1[i][0])  # due to the test with testLen, the first parameter of a couple parameter should be the same as the others
  #nbOfValuesPerParam.append(length_of_list)
  #totalNbOfParamDistribution *= length_of_list
  #for j in range(len(paramValuesList1[i])):
  combinedCouplesList = []
  for k in range(length_of_list):
    combinedCouples = []
    for j in range(len(paramValuesList1[i])):
      combinedCouples.append( paramValuesList1[i][j][k] )
    combinedCouplesList.append(combinedCouples)
  combinedCouplesListOfList.append(combinedCouplesList) 

#print('\ndistributions=')
for element in itertools.product(*combinedCouplesListOfList):
  distribution=[]
  for values in element: #paramValuesList3.append( list(sum(element)) )
    distribution += values
  assert(len(distribution)==len(paramNames2))
  paramValuesList2.append(distribution)
  #print(distribution)

print(len(paramValuesList2))








templateFiles = findParameterLine('templateFiles',fileList)  
templateList = templateFiles.split('=')#[1].strip().split()
#print templateList, templateFiles
#exit()


fileIn  = open('para.dat','r')
#
N=0
for distribution in paramValuesList2:
  directoryName = 'job'+str(N)
  if not os.path.exists(directoryName):
    os.mkdir(directoryName)
  fileOut = open(directoryName+'/'+'para.dat','w')
  

  fileIn.seek(0) #rewind to the beginning of the file
  for line in fileIn:
    for name,value in zip(paramNames2,distribution):
      line =  line.replace('~~'+name+'~~',str(value))
    
    fileOut.write(line)
  
    
  #fileIn.seek(0) #rewind to the beginning of the file
  #for line in fileIn:
  #  lineOut = line.replace('~~'+paramNames2[0]+'~~',str(paramValuesList2[0][0]))
  #  #print lineOut
  #  fileOut.write(lineOut)
  fileOut.close()
  N+=1
  

fileIn.close()
   

