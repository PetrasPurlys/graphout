import multiprocessing
import os
import re
import subprocess
import time


class Measure:

    @classmethod
    def run(cls, command_template: str, command_template_args_1: [], number_of_runs: int, stream: str, pattern_dict: {str: str},
            proc_count: int, quiet: bool, print_progress: bool, no_raw_data: bool, no_proc_time: bool,
            measure_proc_time_name: str) -> [dict]:

        run_dict_list = []
        re_result = re.search(r'\[(.*)\]', command_template)

        if re_result is None or len(command_template_args_1) == 0:
            arg_name = ''
            args     = ['']
            commands = [command_template]
        else:
            arg_name = re_result.groups()[0]
            args     = command_template_args_1
            commands = [command_template.replace(f"[{arg_name}]", arg_1) for arg_1 in args]

        for i, (arg_1, command) in enumerate(zip(args, commands), start=1):
            if not quiet and print_progress:
                print(f"[{i}/{len(commands)}]: {command}", end='\t')

            measure_dict = cls._run_1_config_n_times(
                n=number_of_runs, run_command=command, proc_count=proc_count, stream=stream,
                pattern_dict=pattern_dict, no_proc_time=no_proc_time, measure_proc_time_name=measure_proc_time_name,
                quiet=quiet,
            )

            run_dict = {
                'command': command,
                'x_name':  arg_name,
                'x':       arg_1,
                'measures': {
                    metric: {'stats': cls._get_agg_statistics(points)} | ({'data': points} if not no_raw_data else {})
                    for metric, points in measure_dict.items()
                },
            }

            run_dict_list.append(run_dict)

            if not quiet and print_progress:
                for metric, measure_dict in run_dict['measures'].items():
                    print(f"{metric}: {measure_dict['stats']['cnt']} points", end='\t')
                print()

                for metric, points in measure_dict.items():
                    if len(points) == 0:
                        print(f'No data was captured for {metric=}, command={command}')

        # add a new line after all the progress information has been printed
        if not quiet and print_progress:
            print()

        return run_dict_list

    @classmethod
    def _get_agg_statistics(cls, data_points: [float]) -> dict:
        cnt = len(data_points)
        avg = sum(data_points) / cnt
        std = (sum((x - avg)**2 for x in data_points) / (cnt - 1))**0.5 if cnt > 1 else 'nan'

        return {
            'cnt': cnt,
            'avg': avg,
            'std': std,
            'min': min(data_points),
            'max': max(data_points),
        }

    @classmethod
    def _run_1_config_n_times(cls, n: int, run_command: str, proc_count: int, stream: str, pattern_dict: {str: str},
                              no_proc_time: bool, measure_proc_time_name: str, quiet: bool) -> dict:

        result_dict = {}

        if proc_count == 1:
            measure_dict_list = [
                cls._run_1_config_1_time(
                    command=run_command, stream=stream, pattern_dict=pattern_dict,
                    no_proc_time=no_proc_time, measure_proc_time_name=measure_proc_time_name,
                    quiet=quiet,
                )
                for _ in range(n)
            ]
        else:
            if proc_count == 0:
                proc_count = os.cpu_count()
            elif proc_count < 0:
                proc_count = os.cpu_count() - proc_count

            with multiprocessing.Pool(proc_count) as pool:
                params = [(run_command, stream, pattern_dict, no_proc_time, measure_proc_time_name, quiet)]
                measure_dict_list = pool.starmap(cls._run_1_config_1_time, params * n)

        for measure_dict in measure_dict_list:
            for measure_name, measure_value_list in measure_dict.items():
                if measure_name not in result_dict:
                    result_dict[measure_name] = []
                result_dict[measure_name] += measure_value_list

        return result_dict

    @classmethod
    def _run_1_config_1_time(cls, command: str, stream: str, pattern_dict: {str: str}, no_proc_time: bool,
                             measure_proc_time_name: str, quiet: bool) -> dict:

        time_ns_1 = time.monotonic_ns()
        proc = subprocess.run(command, shell=False, capture_output=True)
        time_ns_2 = time.monotonic_ns()

        if stream == 'out':
            std_lines = proc.stdout.decode().rstrip().splitlines(keepends=False)
        elif stream == 'err':
            std_lines = proc.stderr.decode().rstrip().splitlines(keepends=False)
        elif stream == 'all':
            std_lines = proc.stdout.decode().rstrip().splitlines(keepends=False) \
                      + proc.stderr.decode().rstrip().splitlines(keepends=False)
        else:
            raise ValueError

        result_dict: {str: float} = {}

        unordered_result_dict = {}
        for std_line in std_lines:
            for pattern_name, pattern_reg in sorted(pattern_dict.items(), key=lambda reg: len(reg[1]), reverse=True):
                if (match := re.search(pattern_reg, std_line)) is not None:
                    groups = match.groups()
                    assert len(groups) == 1, "only a single group should match in the pattern regex"
                    measure = float(groups[0])

                    if pattern_name not in unordered_result_dict:
                        unordered_result_dict[pattern_name] = [measure]
                    else:
                        unordered_result_dict[pattern_name].append(measure)

        for x in list(pattern_dict.keys()):
            if x in unordered_result_dict:
                result_dict[x] = unordered_result_dict[x]

        # process lifetime should be the last entry
        if not no_proc_time:
            result_dict[measure_proc_time_name] = [(time_ns_2 - time_ns_1) / 10**9]

        return result_dict
