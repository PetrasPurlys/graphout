import argparse
import os
import platform
from collections import Counter
from typing import List

from graphout import default
from graphout.cli.parameters import (GraphicResults, NumericResults,
                                     Parameters, ProcessLifetime)


class CLI:

    @classmethod
    def parse_args_to_parameters(cls, args: List[str]) -> Parameters:

        cmd_quotes = '"' if platform.system() != 'Windows' else '"""'
        parser = argparse.ArgumentParser(
            prog=default.APP_NAME,
            prefix_chars='-',
            description=f'A benchmarking tool. Can capture, parse and plot stdout and stderr data. {os.linesep}'
                       rf'    {default.APP_NAME} -n 12 --proc 6 --out ping_so -p {cmd_quotes}latency:time=([0-9]*)ms{cmd_quotes} --rot-x -- ping www.stackoverflow.com -l [payload_bytes] -- 100 1000 10000 20000' + f'{os.linesep}',
            formatter_class=argparse.RawTextHelpFormatter,
            add_help=True,
            usage=f'{default.APP_NAME} [options] -- command template -- parameters',
        )
        parser.add_argument('-p',  '--patterns',       type=str, nargs='*', default=[], help=f'regexes defining a group to capture as a metric from std streams', metavar='PATTERNS')
        parser.add_argument('-n',                      type=int, default=default.RUNS,  help=f'number of runs (default={default.RUNS})',                          metavar='N')
        parser.add_argument('-q',  '--quiet',          action='store_true',             help=f'do not print anything')
        parser.add_argument(       '--no-progress',    action='store_true',             help=f'do not print progress information')
        parser.add_argument(       '--no-summary',     action='store_true',             help=f'do not print summary table')
        parser.add_argument(       '--no-results',     action='store_true',             help=f'do not create a measurement result file')
        parser.add_argument(       '--no-raw-data',    action='store_true',             help=f'do not add raw measure data to the result file')
        parser.add_argument(       '--no-graphs',      action='store_true',             help=f'do not create graphs')
        parser.add_argument(       '--no-avg',         action='store_true',             help=f'do not create average graphs')
        parser.add_argument(       '--no-ci',          action='store_true',             help=f'do not add confidence intervals to average graphs')
        parser.add_argument(       '--force-ci',       action='store_true',             help=f'add confidence intervals to average graphs (regardless of measure count)')
        parser.add_argument(       '--no-hist',        action='store_true',             help=f'do not create histograms graphs')
        parser.add_argument(       '--no-kde',         action='store_true',             help=f'do not create kernel density estimate graphs')
        parser.add_argument(       '--no-rug',         action='store_true',             help=f'do not add rug plots (below hist and kde graphs)')
        parser.add_argument(       '--stacked',        action='store_true',             help=f'create a stacked histogram and kde graph')
        parser.add_argument(       '--no-title',       action='store_true',             help=f'do not add command template to graph title')
        parser.add_argument('-lx', '--log-x-axis',     action='store_true',             help=f'use logarithmic x axis')
        parser.add_argument('-ly', '--log-y-axis',     action='store_true',             help=f'use logarithmic y axis')
        parser.add_argument(       '--rot-x',          action='store_true',             help=f'rotate labels of x axis')
        parser.add_argument(       '--res', type=str, default=default.RESULT_FILE_NAME, help=f'result file name', metavar='NAME')
        parser.add_argument(       '--out',            type=str, default='',            help=f'result folder name', metavar='NAME')
        parser.add_argument(       '--proc',           type=int, default=1,             help=f'number of parallel processes to run {{n, 1=none, 0=max, -i=max-i}}', metavar='N')
        parser.add_argument(       '--proc-lifetime',  type=str, default='',            help=f'also measure the lifetime of the process executing the command with the given name', metavar='NAME')
        parser.add_argument(       '--stream',    type=str, default=default.STD_STREAM, help=f'std stream to inspect', choices=['out', 'err', 'all'])

        if '--' not in args:
            parser.print_help()
            exit(1)
        elif default.APP_NAME in args:
            args = args[args.index(default.APP_NAME)+1:]

        # a hack to get around a path being the first argument when executed as a tool
        if default.APP_NAME in args[0]:
            args = args[1:]

        parameter_args, args = args[:args.index('--')], args[args.index('--')+1:]
        if '--' in args:
            command_template = ' '.join(args[:args.index('--')])
            command_args     = args[args.index('--')+1:]
        else:
            command_template = ' '.join(args)
            command_args     = []

        pa, unknowns = parser.parse_known_args(parameter_args)
        if len(unknowns) > 0:
            print("Unknown arguments:", ','.join(unknowns))
            exit(2)

        parameters = Parameters(
            command_template=command_template,
            command_template_args_1=command_args,
            number_of_runs=pa.n,
            capture_patterns=pa.patterns,
            stream=pa.stream,
            parallel_process_count=pa.proc,
            quiet=pa.quiet,
            print_progress=not pa.no_progress,
            print_summary=not pa.no_summary,
            numeric_results=NumericResults(
                no_output=pa.no_results,
                file_name=pa.res,
                folder_name=pa.out,
                no_raw_data=pa.no_raw_data,
            ),
            graphic_results=GraphicResults(
                no_output=pa.no_graphs,
                no_conf_int=pa.no_ci,
                force_conf_int=pa.force_ci,
                no_hist=pa.no_hist,
                no_kde=pa.no_kde,
                no_rug=pa.no_rug,
                create_stacked_hist_kde=pa.stacked,
                no_title=pa.no_title,
                log_x_axis=pa.log_x_axis,
                log_y_axis=pa.log_y_axis,
                rotate_x=pa.rot_x,
            ),
            process_lifetime=ProcessLifetime(
                skip=pa.proc_lifetime == '',
                measurement_name=pa.proc_lifetime,
            ),
        )

        measure_name_list = parameters.get_measure_name_list()
        duplicates = [elem for elem, cnt in Counter(measure_name_list).items() if cnt > 1]
        if duplicates:
            print(f'Duplicate regex patterns found:', os.linesep.join(duplicates), 'Please provide unique values.',
                  sep=os.linesep)
            exit(1)

        return parameters
