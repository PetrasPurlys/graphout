import json
import sys

from tabulate import tabulate

from graphout.app import App
from graphout.cli.cli import CLI
from graphout.graph import Graph
from graphout.measure import Measure


def main():
    prm = CLI.parse_args_to_parameters(args=sys.argv)

    runs_dict = Measure.run(
        command_template=prm.command_template, command_template_args_1=prm.command_template_args_1,
        number_of_runs=prm.number_of_runs, stream=prm.stream, pattern_dict=prm.get_pattern_dict(),
        proc_count=prm.parallel_process_count, quiet=prm.quiet, print_progress=prm.print_progress,
        no_raw_data=prm.numeric_results.no_raw_data, no_proc_time=prm.process_lifetime.skip,
        measure_proc_time_name=prm.process_lifetime.measurement_name,
    )

    result_dict = {
        'base': prm.command_template,
        'runs': runs_dict,
        'args': ' '.join(sys.argv[1:]),
    }

    if not prm.quiet and prm.print_summary:
        table = []
        measure_names = list(result_dict['runs'][0]['measures'].keys())
        stat_names    = list(result_dict['runs'][0]['measures'][measure_names[0]]['stats'].keys())
        headers       = ['command', 'measure'] + stat_names

        for measure in measure_names:
            for run_dict in result_dict['runs']:
                stats = list(run_dict['measures'][measure]['stats'].values())
                row = [run_dict['command'], measure] + stats
                table.append(row)

        print(tabulate(table, headers=tuple(headers)))

    get_out_file_path_fun = lambda fn: App.get_path_to_measurement_result(prm.numeric_results.folder_name, fn)

    with open(get_out_file_path_fun(f'{prm.numeric_results.file_name}.json'), 'w') as f:
        json.dump(result_dict, f, indent=4)

    if not prm.graphic_results.no_output:
        if len(prm.command_template_args_1) > 0:
            for measure_name in prm.get_measure_name_list():
                run_dicts = [run_dict for run_dict in result_dict['runs'] if measure_name in run_dict['measures']]
                if len(run_dicts) == 0:
                    continue

                Graph.render_1d_measure_avg_ci(
                    measure_name=measure_name,
                    run_dicts=run_dicts,
                    command_base=result_dict['base'],
                    out_file_path=get_out_file_path_fun(f'{measure_name}_avg.png'),
                    include_ci=prm.graphic_results.get_include_ci(),
                    no_title=prm.graphic_results.no_title,
                    log_x=prm.graphic_results.log_x_axis,
                    log_y=prm.graphic_results.log_y_axis,
                    rotate_x=prm.graphic_results.rotate_x,
                )

        run_dicts = result_dict['runs']
        for measure_name in run_dicts[0]['measures'].keys():
            for run_dict in run_dicts:
                if "x" not in run_dict:
                    continue

                if not prm.graphic_results.no_hist:
                    out_file_path = get_out_file_path_fun(f'{measure_name}_{run_dict["x"]}_hist.png')
                    Graph.render_histogram(
                        measure_name=measure_name, run_dicts=[run_dict], out_file_path=out_file_path,
                        skip_rug=prm.graphic_results.no_rug,
                    )

                if not prm.graphic_results.no_kde:
                    out_file_path = get_out_file_path_fun(f'{measure_name}_{run_dict["x"]}_kde.png')
                    Graph.render_kernel_density_estimate(
                        measure_name=measure_name, run_dicts=[run_dict], out_file_path=out_file_path,
                        skip_rug=prm.graphic_results.no_rug,
                    )

                if prm.graphic_results.create_stacked_hist_kde:
                    out_file_path = get_out_file_path_fun(f'{measure_name}_{run_dict["x"]}_stacked.png')
                    Graph.render_stacked_hist_kde(
                        measure_name=measure_name, run_dicts=[run_dict], out_file_path=out_file_path,
                        skip_rug=prm.graphic_results.no_rug,
                    )

            if not prm.graphic_results.no_hist:
                out_file_path = get_out_file_path_fun(f'{measure_name}_hist.png')
                Graph.render_histogram(
                    measure_name=measure_name, run_dicts=run_dicts, out_file_path=out_file_path,
                    skip_rug=prm.graphic_results.no_rug,
                )

            if not prm.graphic_results.no_kde:
                out_file_path = get_out_file_path_fun(f'{measure_name}_kde.png')
                Graph.render_kernel_density_estimate(
                    measure_name=measure_name, run_dicts=run_dicts, out_file_path=out_file_path,
                    skip_rug=prm.graphic_results.no_rug,
                )

            if prm.graphic_results.create_stacked_hist_kde:
                out_file_path = get_out_file_path_fun(f'{measure_name}_stacked.png')
                Graph.render_stacked_hist_kde(
                    measure_name=measure_name, run_dicts=run_dicts, out_file_path=out_file_path,
                    skip_rug=prm.graphic_results.no_rug,
                )


if __name__ == '__main__':
    main()
