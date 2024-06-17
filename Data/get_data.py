from logging import config
import sys
import getopt
import functools
import operator
from queue import Queue
import os
from pathlib import Path
import csv
import re
from tabnanny import check
from openpyxl import Workbook
import shutil
import math
  
def tikz_cactus_header(title,xlabel,ylabel, ymin=0,ymax=1000):
  return "\\begin{figure}\n% \\centering\n% \\begin{subfigure}[b]{.49\textwidth}\n\\centering\n\\begin{tikzpicture}[scale = 1.05]\n\\begin{axis}[mark options={scale=1.0},grid=both, grid style={black!10},  legend style={at={(0.9,0.2)}}, legend cell align={left},\nx post scale=1,xlabel="+xlabel+",ylabel="+ylabel+",mark size=3pt,    height=12cm,width=12cm,ymin="+str(ymin)+",ymax="+str(ymax)+",xmin=0.1,xmax=6000,title={"+title+"}]\n  \n"

def tikz_scatter_header(title,xlabel,ylabel):
  return "\\begin{figure}\n% \\centering\n\\begin{tikzpicture}[scale = 1.05]\n\\begin{axis}[mark options={scale=1.0},grid=both, grid style={black!10},  legend style={at={(0.9,0.2)}}, legend cell align={left},\nx post scale=1,xlabel="+xlabel+", ylabel="+ylabel+",mark size=3pt, xmode=log,    ymode=log,height=12cm,width=12cm,xmin=0.1,xmax=6000,ymin=0.1,ymax=6000,title={"+title+"}]\n"
 
def tikz_ender():
  return  "\\end{axis}\n\\end{tikzpicture}\n\\end{figure}"

def tikz_scatter_ender():
  return  "\\addplot[color=black] coordinates {(0.009, 0.009) (5000, 5000)};\n\\addplot[color=black, dashed] coordinates {(0.009, 5000) (5000, 5000)};\n\\addplot[color=black, dashed] coordinates {(5000, 0.009) (5000, 5000)};\n\\legend{SAT, UNSAT}\n\\end{axis}\n\\end{tikzpicture}\n\\end{figure}"

def trim(s):
    while len(s) > 0 and s[-1] in '\r\n':
        s = s[:-1]
    return s
    
def strip_lead(s):
  skip = True
  new_s = ""
  for i in range(len(s)-1,0,-1):
    if skip:
      if s[i] == '.': skip = False
    else:
      if s[i] == '/':
       
        if new_s[-4:] == ".cnf":
          new_s = new_s[:-4]
        return(new_s)
      else: new_s = s[i] + new_s


def get_config_table_name (name):
  names = {"ccdcl":"\\ccdcl{}" , "ccdclPlus":"\\ccdcl+NoModes{}" , "ccdclPlusModes":"\\ccdclPlus{}" , "cadical":"\\cadical{}", "reencode":"\\reencode{}", "sat4j":"\\satj{}", "roundingSAT":"\\roundingSAT{}"}
  return names[name]
  
def print_new_squares(stat_con, configurations):
## Tikz table formatting

  print("Magic Squares")
  print(list(range(5,13)))
  for c in configurations:
    st = get_config_table_name(c) + " "
    for n in range(5,13):
      b = "magicsq-"+str(n)
      t = get_time_value (stat_con[b][c])
      result = get_result_value(stat_con[b][c])
      if t < 5000 and result > -1:
        st += " & " + str(round(t ,2))
      else:
        st += " & -- "
    print(st + " \\\\")

  print("\nMax Squares")
  print(str([(7,32),(8,41),(9,51),(10,61),(7,33),(8,42),(9,52),(10,62)]))
  for c in configurations:
    st = get_config_table_name(c) + " "
    for n,m in [(7,32),(8,41),(9,51),(10,61)]:
      b = "maxsquare-"+str(n)+"-"+str(m)+"-SAT"
      t = get_time_value (stat_con[b][c])
      result = get_result_value(stat_con[b][c])
      if t < 5000 and result > -1:
        st += " & " + str(round(t ,2))
      else:
        st += " & -- "
    for n,m in [(7,33),(8,42),(9,52),(10,62)]:
      b = "maxsquare-"+str(n)+"-"+str(m)+"-UNSAT"
      t = get_time_value (stat_con[b][c])
      result = get_result_value(stat_con[b][c])
      if t < 5000 and result > -1:
        st += " & " + str(round(t ,2))
      else:
        st += " & -- "
    print(st+ " \\\\")



def print_scatter(solve_stats,extractor,card_sizes,config1,config2, benchmarks):
  colors = ["blue","redpurple","midgreen","clearorange","clearyellow","darkestblue", "browngreen","redpurple","black","darkred"]
  marks = ["diamond",""]
  cnt = 0

  data_list = []
  
  for b in benchmarks:

    # if max(int(extractor[b]['DirMax']),int(extractor[b]['EncMax']) ) < 10: continue

    # if gt5:
    #   if max(int(extractor[b]['DirMax']),int(extractor[b]['EncMax']) ) < 5: continue 
    # elif not 
    if not size_above (card_sizes[b],10,10): continue

    cnt += 1
    
    exMark = False

    if config1 not in solve_stats[b]:
      print(f'{config1} {b}')
    if config2 not in solve_stats[b]:
      print(f'{config2} {b}')

    result1 = get_result_value (solve_stats[b][config1])
    result2 = get_result_value (solve_stats[b][config2])
    truth_value = max(result1, result2)

    time1 = get_time_value (solve_stats[b][config1])
    time2 = get_time_value (solve_stats[b][config2])
        
    if truth_value == -1: continue # both timeouts


    if time1 < 0.1: time1 = 0.1 # lift to 0.1 so it is shown on the scatter plot
    if time2 < 0.1: time2 = 0.1
    if time1 >= 5000: time1 = 5000 # timeout
    if time2 >= 5000 : time2 = 5000
    if result1 == -1: time1 = 5000
    if result2 == -1: time2 = 5000
    if time1 == 5000 and time2 == 5000 : continue # point at top right diagonal
    if time1 == 0.1 and time2 == 0.1 : continue # point at bottom left diagonal

    # ratio = math.sqrt(get_number_above(card_sizes[b],10))

    ratio = pow(get_number_above(card_sizes[b],10), (1/4))

    ratio = min (ratio,10)
    if ratio < 1:
      ratio = 1
    
    color_mark = truth_value
    
    plot = "\\addplot[color="+colors[color_mark]+",mark="+marks[truth_value]+"*,mark size="+str(ratio)+"pt,opacity=0.5] coordinates { "
    plot += "("+str(time1) + "," + str(time2) + ") };"
    
    print(plot)

  print("\n\n\n\n\n\n")
    
  return cnt



def print_cactus (input_card_stats,ratios, solve_stats, sat):
  colors = ["blue","redpurple","midgreen","clearorange","clearyellow","darkestblue", "browngreen","redpurple","black","darkred"]
  marks = ["diamond*","square*", "x", "o","star"]
  
  
  configurations = ["ccdcl","ccdclPlus","ReEncode","cadical"]

  config_times = {}
  config_totals = []

  

  for c in configurations:
    config_times[c] = []
    for b in input_card_stats.keys():

      if int (max(input_card_stats[b]['DirMax'],input_card_stats[b]['EncMax'])) < 10: continue
      if float(input_card_stats[b]['AvgSize']) < 3.5: continue

      truth_value = -1
      result = solve_stats[b]['result']
      if result == "UNSAT":
        truth_value = 1
      if result == "SAT":
        truth_value = 0


      if sat and truth_value == 1: continue
      if not sat and truth_value == 0: continue
     

      time = float(solve_stats[b][c]['CPU'])
      if time < 5000: 
        config_times[c].append(time)
    config_totals.append((c,len(config_times[c])))

  # sort
  sorted_configs = sorted(config_totals,reverse=True, key=lambda v: v[1])

  if sat: print(tikz_cactus_header ("SAT with avg filter","time (s)", "number solved",300,380))
  else: print(tikz_cactus_header ("UNSAT with avg filter","time (s)", "number solved",0,250))
  

  legend = []
  pos = -1
  for c,t in sorted_configs:
    legend.append(c.replace("_","-"))
    cnt = 1
    pos += 1
    config_times[c].sort()
    st = ""
    print ("\\addplot[color="+colors[configurations.index(c)]+",mark="+marks[configurations.index(c)%len(marks)]+",opacity=0.5] coordinates { ")
    for time in config_times[c]:
      st += ("("+str(time) + "," + str(cnt) + ") ")
      cnt += 1
    st += ("("+str(6000) + "," + str(cnt-1) + ") };")
    print (st)

  
  print("\\legend{"+", ".join(legend)+"}")

  print(tikz_ender())

def check_benchmark_failed (line):
  if "failed" in line['result']:
    return True 
  
  return False

def get_failed_benchmarks(configuration, solve_stats):
  failed_list = []
  for b in solve_stats.keys():
    d = solve_stats[b][configuration]
    if check_benchmark_failed (d):
      failed_list.append (b)

  return failed_list

def get_all_failed_benchmarks (failed_lists):
  return list (set([b for b in l for l in failed_lists]))

def size_above (d, size, cnt):
  dAbove = 0
  eAbove = 0
  for (s,c) in d['d']:
    if s >= size:
      dAbove += c
  for (s,c) in d['e']:
    if s >= size:
      eAbove += c
  
  if eAbove + dAbove >= cnt: return True
  else: return False

def get_number_above (d, size):
  dAbove = 0
  eAbove = 0
  for (s,c) in d['d']:
    if s >= size:
      dAbove += c
  for (s,c) in d['e']:
    if s >= size:
      eAbove += c
  
  return dAbove + eAbove

def get_sizes (tokens):
  ds = []
  es = []
  get_es = False
  size = -1 
  for t in tokens:
    if t == "E":
      get_es = True
    elif t =="D":
      continue
    else:
      if size == -1:
        size = int (t)
      else:
        cnt = int(t)
        if get_es:
          es.append((size,cnt))
        else:
          ds.append((size,cnt))
        size = -1
  
  return {'d':ds, 'e':es}


def get_extraction_sizes (csv_file):
  file = open(csv_file,'r')
  data = {}
  for line in file:
    line = trim(line)
    tokens = line.split()
    if len(tokens) < 2: continue
    b = tokens[0]
    data[b] = get_sizes(tokens[1:])
  return data

def get_extractor_csv_data(csv_file):
  candidates = []
  stats = {}
  with open(csv_file, mode='r') as csvFile:
    csvReader = csv.DictReader(csvFile)
    for line in csvReader:
      b = line["Name"]
      candidates.append(b)
      if b in stats: 
        print(f"ERROR: Repeated formula {b}")
      stats[b] = line
  return {'candidates':candidates, 'stats':stats}


def get_new_extractor_csv_data(csv_file):
  candidates = []
  stats = {}
  with open(csv_file, mode='r') as csvFile:
    csvReader = csv.DictReader(csvFile)
    for line in csvReader:
      b = line["Name"]
      candidates.append(b)
      # if b in stats: 
      #   print(f"ERROR: Repeated formula {b}")
      stats[b] = line
  return {'candidates':candidates, 'stats':stats}


def get_squares_csv_data(csv_file):
  candidates = []
  configurations = []
  stats = {}
  with open(csv_file, mode='r') as csvFile:
    csvReader = csv.DictReader(csvFile)
    for line in csvReader:
      b = clean_benchmark_name(line["Name"])
      config = get_benchmark_config (line["Name"])
      if config not in configurations: 
        configurations.append(config)
      if b not in candidates:
        candidates.append(b)
      if not b in stats: stats[b] = {}
      if config in stats[b]: 
        print(f"ERROR: Repeated formula {b} in configuration {config}")
      stats[b][config] = line
  return {'candidates':candidates, 'stats':stats, 'configurations':configurations}

# def get_solver_csv_data(csv_file, config):
#   candidates = []
#   configurations = []
#   stats = {}
#   with open(csv_file, mode='r') as csvFile:
#     csvReader = csv.DictReader(csvFile)
#     for line in csvReader:
#       b = clean_benchmark_name(line["Name"])
#       # config = line['config']
#       # if config not in configurations: 
#       #   configurations.append(config)
#       if b in candidates:
#         print(f"ERROR: duplicate benchmark {b}")
#       candidates.append(b)
#       if not b in stats: stats[b] = {}
#       if config in stats[b]: 
#         print(f"ERROR: Repeated formula {b} in configuration {config}")
#       stats[b][config] = line
#   return {'candidates':candidates, 'stats':stats, 'configurations':[config]}



def get_mixed_solver_csv_data(csv_file):
  candidates = []
  configurations = []
  stats = {}
  with open(csv_file, mode='r') as csvFile:
    csvReader = csv.DictReader(csvFile)
    for line in csvReader:
      config = get_benchmark_config (line["Name"])
      b = clean_benchmark_name(line["Name"])
      if config not in configurations: 
        configurations.append(config)
      if b not in candidates:
        # print(f"ERROR: duplicate benchmark {b}")
        candidates.append(b)
      if not b in stats: stats[b] = {}
      if config in stats[b]: 
        print(f"ERROR: Repeated formula {b} in configuration {config}")
      stats[b][config] = line
  return {'candidates':candidates, 'stats':stats, 'configurations':configurations}

def get_result_valueP (data) :
  if  data == "SATISFIABLE":
    return 0
  elif data == "UNSATISFIABLE":
    return 1
  else:
    return -1


def get_result_value (data) :
  if  data == "SATISFIABLE" or data['Result'] == "SAT":
    return 0
  elif data == "UNSATISFIABLE" or data['Result'] == "UNSAT":
    return 1
  else:
    return -1
  
def get_time_value (data) :
  return round(float(data['Time']),2)

def get_benchmark_config (name):
  ends = ["-noDecide0","-noDecide1"]
  for e in ends:
    name = clean_end ( name, e)
  configs = ["-ccdcl","-cadical", "-ccdclPlus ", "-ccdclPlus", "-ccdclPlusModes ", "-ccdclPlusModes","-reencode","-sat4j", "-roundingSAT"]
  for c in configs:
    if name.endswith(c):
      return (c[1:])

def clean_end (name, e):
  if name.endswith(e):
    name = name.replace(e, '')
  return name

def clean_benchmark_name (name):
  in_name = name
  ends = ["-ccdcl","-cadical", "-ccdclPlus ", "-ccdclPlus", "-ccdclPlusModes ", "-ccdclPlusModes","-reencode","-sat4j", "-roundingSAT","-noDecide0","-noDecide1", "-ccdclPlusModesDelete"]
  for e in ends:
    name = clean_end (name, e)
  if in_name != name:
    return clean_benchmark_name (name)
  return name


def print_extractor_table (candidates, extractor,extractor_header, extraction_sizes):
  nAny = 0
  nDirectExcl = 0
  nEncodedExcl = 0
  nBoth = 0
  nEncodedK = [0,0,0,0]
  nBelow = 0
  avgRuntime = 0
  nBelowtens = 0
  
  nAboveFive = 0
  nAboveTen = 0
  cnt = 0

  for b in candidates:
    
   
    dh = extractor_header[b]
    cnt += 1

    avgRuntime += float(dh['real_time'])
    if float(dh['real_time']) <= 15: nBelowtens += 1

    if b not in extractor: continue

    d = extractor[b]

    if max(int(extractor[b]['DirMax']),int(extractor[b]['EncMax']) ) >= 5:
      nAboveFive += 1

    if size_above (extraction_sizes[b],10,10):
      nAboveTen += 1

    

    if int(d['dAmoCnt']) > 0 or int(d['eAmoCnt']) > 0:
      nAny += 1
      if int(d['dAmoCnt']) > 0 and int(d['eAmoCnt']) > 0:
        nBoth += 1
      elif int(d['eAmoCnt']) > 0:
        nEncodedExcl += 1
      else:
        nDirectExcl += 1
    if int(d['eAmoCnt']) > 0:
      kRatio = int(d['EncodeWeightSumK']) / float(d['ElimVars'])
      if kRatio < 1.5: nEncodedK[0] += 1
      elif kRatio < 2.5: nEncodedK[1] += 1
      elif kRatio < 3.5: nEncodedK[2] += 1
      elif kRatio < 4.5: nEncodedK[3] += 1
      else : # extra large ratio
        nEncodedK[3] += 1
  print(f'Total {cnt}')
  print("Found, Pairwise, Auxiliary, Both, AMO >= 5, AMO >= 10 x 10, Avg. (s), <= 15 s")
  print((nAny,nDirectExcl,nEncodedExcl,nBoth,nAboveFive, nAboveTen,round(avgRuntime/cnt,0), round(100 * nBelowtens/cnt, 0)))
  print(f"per5 {nAboveFive*1.0/cnt} per10x10 {nAboveTen*1.0/cnt}")
  # print("table 5, encoded ratios")
  # print(nEncodedK)

def print_solved_table (candidates, stats,configurations,extractor, extraction_sizes,gt5=True, timeout=5000, SAT=True, UNSAT=True):
  par2 = {}
  solved = {}
  total_solved = [0,0]
  for c in configurations:
    par2[c] = [0,0] # 0: SAT, 1: UNSAT
    solved[c] = [0,0] # 0: SAT, 1: UNSAT
  cnt = 0
  failed = 0
  fail_cnt = 0
  
  for b in candidates:

    if gt5:
      if max(int(extractor[b]['DirMax']),int(extractor[b]['EncMax']) ) < 5: continue 
    elif not size_above (extraction_sizes[b],10,10): continue

    cnt += 1
    result = -1 # -1: unknown, 0: SAT, 1: UNSAT

    failed_script = False
    
    for c in configurations:
      if c not in stats[b]:
        print(f"c not in stats {b} {c}")
        continue
      d = stats[b][c]
      if d['Completed'] != "Success": 
        failed += 1
        failed_script = True
        continue
      c_result = get_result_value(d)
      if result == -1:
        result = c_result
      elif c_result > -1:
        if result > -1 and result != c_result:
          print(f"ERROR: mismatched result for benchmark {b}")
    
    if failed_script: 
      print("Failed")
      continue

    if result > -1:
      total_solved[result] += 1

    # get times
    for c in configurations:
      if c not in stats[b]:
        print(f"{b} {c}")
        continue
      d = stats[b][c]
      # if "Time" not in d:/ continue
      # if d['Completed'] != "Success": continue
      time = get_time_value(d)
      c_result = get_result_value(d)
      if time >= timeout:
        # if c_result == -1:
        #   print(f"{c} {time} {c_result} {b}")
        c_result = -1
      if time < timeout - 2500 and c_result == -1 :
        fail_cnt += 1
        if c != "sat4j":
          print(f"ERROR: runtime below timeout but result failure for config {c} for benchmark {b}")
      if c_result > -1:
        par2[c][c_result] += time
        solved[c][c_result] += 1
      elif result > -1:
        par2[c][result] += 2*timeout

  # print(total_solved, par2, solved)
  # print tables
  print("")
  print(f'{fail_cnt}')
  print(f'{cnt} {failed}')
  print(f'total SAT {total_solved[0]} UNSAT {total_solved[1]}')
  print("SAT UNSAT TOTAL PAR2_SAT PAR2_UNSAT PAR2_TOTAL CONFIG")
  for c in configurations:
    # print(f'{solved[c][0]} {solved[c][1]} {solved[c][0]+solved[c][1]} {round(par2[c][0]/total_solved[0],2)} {round(par2[c][1]/total_solved[1],2)} {round((par2[c][0] + par2[c][1])/(total_solved[0]+total_solved[1]),2)} {c}')
    name = get_config_table_name (c)
    print(f'{name} & {solved[c][0]} / {solved[c][1]} & {round(par2[c][0]/total_solved[0],2)} & {round(par2[c][1]/total_solved[1],2)} & {round((par2[c][0] + par2[c][1])/(total_solved[0]+total_solved[1]),2)} \\\\')
    

def check_different_extraction (statsO, statsN):
  if statsO['KClauses'] != statsN['KClauses']:
    return True
  elif statsO['dAmoCnt'] != statsN['dAmoCnt']:
    return True
  elif statsO['eAmoCnt'] != statsN['eAmoCnt']:
    return True
  elif statsO['DirMax'] != statsN['DirMax']:
    return True
  elif statsO['EncMax'] != statsN['EncMax']:
    return True
  elif statsO['ElimVars'] != statsN['ElimVars']:
    return True

  return False


def get_data(plots,tables):

  full_data = {}
  ext_data = {}

  ext_data['extraction-1-11'] = get_extractor_csv_data ("CSVs/extraction-full.csv")

  ext_data['extraction-header-1-11'] = get_extractor_csv_data ("CSVs/extraction-header.csv")

  new_data = get_mixed_solver_csv_data ("CSVs/solving.csv")

  extraction_sizes = get_extraction_sizes ("CSVs/extraction-sizes.csv")

  squares_data = get_squares_csv_data("CSVs/squares.csv")
  
  real_stats = {}
  real_configs = []

  # remove unit propagated formulas
  fail_forms = ["18e86b73af9b6adadc355a281387348b-zfcp"] 

  for f in fail_forms:
    ext_data['extraction-header-1-11']['candidates'].remove(f)

  for b in new_data["candidates"]:
    if b not in real_stats:
      real_stats[b] = {}
    for c in new_data["configurations"]:
      if c not in real_configs:
        real_configs.append(c)
      if c not in new_data['stats'][b]:
        print(f"{c} {b}")
      real_stats[b][c] = new_data['stats'][b][c]

  if tables:

    print_extractor_table (ext_data['extraction-header-1-11']['candidates'], ext_data['extraction-1-11']['stats'], ext_data['extraction-header-1-11']['stats'], extraction_sizes)
   
    print_new_squares(squares_data['stats'], squares_data['configurations'])
    
    
    print_solved_table ( ext_data['extraction-1-11']['candidates'] ,real_stats, real_configs,ext_data['extraction-1-11']['stats'], extraction_sizes,True)

    print_solved_table ( ext_data['extraction-1-11']['candidates'] ,real_stats, real_configs,ext_data['extraction-1-11']['stats'], extraction_sizes,False)


  if plots:
    # tikz_header_info = {'title':"Display Size = AvgSize sqrt (gte 10 benchmark set)",\
    #                     'xlabel':'\\cadical{}',\
    #                     'ylabel':'\\ccdclPlus{}',\
    #                     'xmin':0.1,'xmax':6000,'ymin':0.1,'ymax':6000}

    # print(tikz_scatter_header(tikz_header_info['title'],tikz_header_info['xlabel'],tikz_header_info['ylabel']))
    # print_scatter (real_stats,ext_data['extraction-1-11']['stats'], extraction_sizes,"cadical","ccdclPlusModes",ext_data['extraction-1-11']['candidates'])
    # print(tikz_scatter_ender())


    tikz_header_info = {'title':"Display Size = AvgSize sqrt (gte 10 benchmark set)",\
                        'xlabel':'\\ReEncode{}',\
                        'ylabel':'\\ccdclPlus{}',\
                        'xmin':0.1,'xmax':6000,'ymin':0.1,'ymax':6000}

    print(tikz_scatter_header(tikz_header_info['title'],tikz_header_info['xlabel'],tikz_header_info['ylabel']))
    cnt = print_scatter (real_stats,ext_data['extraction-1-11']['stats'], extraction_sizes,"reencode","ccdclPlus",ext_data['extraction-1-11']['candidates'])
    print(tikz_scatter_ender())
    print (cnt)

    # tikz_header_info = {'title':"Display Size = AvgSize sqrt (gte 10 benchmark set)",\
    #                     'xlabel':'\\ReEncode{}',\
    #                     'ylabel':'\\ccdclPlus{}',\
    #                     'xmin':0.1,'xmax':6000,'ymin':0.1,'ymax':6000}

    # print(tikz_scatter_header(tikz_header_info['title'],tikz_header_info['xlabel'],tikz_header_info['ylabel']))
    # print_scatter (real_stats,ext_data['extraction-1-11']['stats'], extraction_sizes,"cadical","reencode",ext_data['extraction-1-11']['candidates'])
    # print(tikz_scatter_ender())


    # tikz_header_info = {'title':"Display Size = AvgSize sqrt (gte 10 benchmark set)",\
    #                     'xlabel':'\\ReEncode{}',\
    #                     'ylabel':'\\ccdclPlus{}',\
    #                     'xmin':0.1,'xmax':6000,'ymin':0.1,'ymax':6000}

    # print(tikz_scatter_header(tikz_header_info['title'],tikz_header_info['xlabel'],tikz_header_info['ylabel']))
    # cnt = print_scatter (real_stats,ext_data['extraction-1-11']['stats'], extraction_sizes,"ccdcl","ccdclPlusModes",ext_data['extraction-1-11']['candidates'])
    # print(tikz_scatter_ender())
    # print(cnt)
  

  
  
  
 

    
#######################################################################################
# MAIN FUNCTION
#######################################################################################
  
def run(name, args):
    
    plots = False
    tables = False

    optlist, args = getopt.getopt(args, "pt")
    for (opt, val) in optlist:
      if opt == '-p':
          plots = True
      elif opt == '-t':
          tables = True

    get_data (plots,tables)
        

if __name__ == "__main__":
    run(sys.argv[0], sys.argv[1:])
