#!/usr/bin/env python
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import getopt
import os
import subprocess
import sys

import onnx

import tensorflow as tf

import opset_version


def main(docs_dir):
  base_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
  docs_dir = os.path.join(base_dir, 'doc')
  onnx_version = ''
  onnx_tf_release_build = False

  try:
    opts, args = getopt.getopt(sys.argv[1:], 'hv:r',
                               ['onnx_version=', 'onnx_tf_release_build'])
  except getopt.GetoptError:
    print('Usage:')
    print('     gen_status.py -v <onnx_version> [-r]')
    print('     gen_status.py -h')
    print('Description:')
    print('  -v, --onnx_version             installed ONNX version')
    print('  -r, --onnx_tf_release_build    create report for ONNX-TF release with version stated in the VERSION_NUMBER file')
    print('                                 when omitted, the report is for ONNX-TF master')
    print('  -h                             show this help message and exit')
    print('eg. generate support_status.md for onnx-tf master and onnx master')
    print('        gen_status.py -v master')
    print('    generate support_status_<onnx_tf_version>.md for onnx-tf ' +
          'version stated in the VERSION_NUMBER file and onnx v1.5.0 ')
    print('        gen_status.py -v v1.5.0 -r')
    sys.exit(2)
  for opt, arg in opts:
    if opt == '-h':
      print('Usage:')
      print('     gen_status.py -v <onnx_version> [-r]')
      print('     gen_status.py -h')
      print('Description:')
      print('  -v, --onnx_version             installed ONNX version')
      print('  -r, --onnx_tf_release_build    create report for ONNX-TF release with version stated in the VERSION_NUMBER file')
      print('                                 when omitted, the report is for ONNX-TF master')
      print('  -h                             show this help message and exit')
      print('eg. generate support_status.md for onnx-tf master and onnx master')
      print('        gen_status.py -v master')
      print('    generate support_status_<onnx_tf_version>.md for onnx-tf ' +
            'version stated in the VERSION_NUMBER file and onnx v1.5.0')
      print('        gen_status.py -v v1.5.0 -r')
      sys.exit()
    elif opt in ('-v', '--onnx_version'):
      onnx_version = arg
    elif opt in ('-r', '--onnx_tf_release_build'):
      onnx_tf_release_build = True
  if onnx_version == '':
    print('Please provide the onnx_version.')
    print('Usage:')
    print('     gen_status.py -v <onnx_version> [-r]')
    print('     gen_status.py -h')
    print('Description:')
    print('  -v, --onnx_version             installed ONNX version')
    print('  -r, --onnx_tf_release_build    create report for ONNX-TF release with version stated in the VERSION_NUMBER file')
    print('                                 when omitted, the report is for ONNX-TF master')
    print('  -h                             show this help message and exit')
    print('eg. generate support_status.md for onnx-tf master and onnx master')
    print('        gen_status.py -v master')
    print('    generate support_status_<onnx_tf_version>.md for onnx-tf ' +
          'version stated in the VERSION_NUMBER file and onnx v1.5.0')
    print('        gen_status.py -v v1.5.0 -r')
    sys.exit(2)

  gen_support_status(docs_dir, onnx_version, onnx_tf_release_build)


def gen_support_status(docs_dir, onnx_version, onnx_tf_release_build):

  # set filename
  if onnx_tf_release_build:
    # get onnx-tf version from VERSION_NUMBER file
    version_dir = os.path.dirname(
        os.path.dirname(os.path.realpath('VERSION_NUMBER')))
    version_file = os.path.join(version_dir, 'VERSION_NUMBER')
    onnx_tf_version = subprocess.check_output('cat ' + version_file, shell=True)
    onnx_tf_version = 'v' + onnx_tf_version.decode().strip('\n')
    filename = 'support_status_' + onnx_tf_version.replace('.', '_') + '.md'
  else:  # onnx-tf = master
    # get onnx-tf commit id
    onnx_tf_commit_id = subprocess.check_output('git rev-parse HEAD',
                                                shell=True)
    onnx_tf_commit_id = onnx_tf_commit_id.decode().strip('\n')
    onnx_tf_version = 'Master ( commit id: {} )'.format(onnx_tf_commit_id)
    filename = 'support_status.md'

  with open(os.path.join(docs_dir, filename), 'w') as status_file:
    status_file.write('# ONNX-Tensorflow Support Status\n')
    status_file.write('|||\n')
    status_file.write('|-:|:-|\n')
    status_file.write('|ONNX-Tensorflow Version|{}|\n'.format(onnx_tf_version))

    # get onnx commit id
    if onnx_version == 'master':
      onnx_path = os.path.dirname(
          os.path.dirname(os.path.realpath(onnx.__file__)))
      onnx_commit_id = subprocess.check_output('cd ' + onnx_path +
                                               '; git rev-parse HEAD',
                                               shell=True)
      onnx_commit_id = onnx_commit_id.decode().strip('\n')
      status_file.write(
          '|ONNX Version|Master ( commit id: {} )|\n'.format(onnx_commit_id))
    else:
      status_file.write('|ONNX Version|{}|\n'.format(onnx_version))

    # get tf_version
    status_file.write('|Tensorflow Version|v{}|\n\n'.format(tf.__version__))

    # display the table legend
    status_file.write('Notes:\n')
    status_file.write('* Values that are new or updated from a ')
    status_file.write('previous opset version are in bold.\n')
    status_file.write('* -: not defined in corresponding ONNX ')
    status_file.write('opset version\n')
    status_file.write('* \*: the operator is deprecated\n')
    status_file.write('* :small_red_triangle:: not supported yet\n')
    status_file.write('* :small_orange_diamond:: partially supported\n')
    status_file.write('* the rest are all supported\n\n')

    # get oll onnx ops
    onnx_ops = {}
    for schema in onnx.defs.get_all_schemas():
      if schema.domain == '':  # only get onnx ops
        onnx_ops[schema.name] = {
            'versions': [],
            'deprecated': schema.since_version if schema.deprecated else -1
        }
    for schema in onnx.defs.get_all_schemas_with_history():
      if schema.domain == '':  # only get onnx ops
        op = onnx_ops[schema.name]
        versions = op['versions']
        versions.append(schema.since_version)

    # get all onnx-tf supported ops
    onnx_tf_ops = opset_version.backend_opset_version
    onnx_tf_ops_ps = opset_version.backend_partial_support

    # get the cureent opset version
    current_opset = onnx.defs.onnx_opset_version()

    # setup table header
    status_file.write('||')
    for i in range(current_opset):
      status_file.write('|')
    status_file.write('\n|:-:|')
    for i in range(current_opset):
      status_file.write(':-:|')
    status_file.write('\n|**ONNX Operator**|')
    for opset in range(1, current_opset + 1):
      status_file.write('**Opset {}**|'.format(opset))

    ops_count = len(onnx_ops)
    # fill in data for the table
    for key, val in sorted(onnx_ops.items()):
      try:
        status_file.write('\n|{}|'.format(key))
        i = 0
        vers = val['versions']
        deprecated = val['deprecated']
        for opset in range(1, current_opset + 1):
          if i <= len(vers) - 1:
            lb = vers[i]
            ub = vers[i + 1] if i < len(vers) - 1 else vers[i]
            if opset < lb:
              if i == 0:
                status_file.write('-')
            elif opset == lb:
              status_file.write('**{}**'.format(lb))
              if lb == deprecated:
                status_file.write('\*')
              elif lb not in onnx_tf_ops[key]:
                status_file.write(':small_red_triangle:')
                if opset == current_opset:
                  ops_count -= 1
              elif key in onnx_tf_ops_ps:
                status_file.write(':small_orange_diamond:')
            else:  # opset > lb
              if opset < ub:
                status_file.write('{}'.format(lb))
                if lb == deprecated:
                  status_file.write('\*')
                elif lb not in onnx_tf_ops[key]:
                  status_file.write(':small_red_triangle:')
                  if opset == current_opset:
                    ops_count -= 1
                elif key in onnx_tf_ops_ps:
                  status_file.write(':small_orange_diamond:')
              elif opset == ub:
                status_file.write('**{}**'.format(ub))
                if ub == deprecated:
                  status_file.write('\*')
                elif ub not in onnx_tf_ops[key]:
                  status_file.write(':small_red_triangle:')
                  if opset == current_opset:
                    ops_count -= 1
                elif key in onnx_tf_ops_ps:
                  status_file.write(':small_orange_diamond:')
                i += 1
              else:  #opset > ub
                status_file.write('{}'.format(ub))
                if ub == deprecated:
                  status_file.write('\*')
                elif ub not in onnx_tf_ops[key]:
                  status_file.write(':small_red_triangle:')
                  if opset == current_opset:
                    ops_count -= 1
                elif key in onnx_tf_ops_ps:
                  status_file.write(':small_orange_diamond:')
            status_file.write('|')
      except:
        # ops defined in onnx but not in opset_version.backend_opset_versionn
        status_file.write(':small_red_triangle:|')

    status_file.write(
        '\n\nONNX-TF Supported Operators / ONNX Operators: {} / {}'.format(
            ops_count, len(onnx_ops)))

    # display partial support footnote
    status_file.write('\n\nNotes:\n')
    index = 1
    for key in onnx_tf_ops_ps:
      status_file.write(
          str(index) + '. ' + key + ': ' + onnx_tf_ops_ps[key] + '\n')
      index += 1


if __name__ == '__main__':
  main(sys.argv[1:])
