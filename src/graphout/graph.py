import matplotlib.pyplot as plt
import seaborn as sns

from graphout import default


class Graph:

    @classmethod
    def render_1d_measure_avg_ci(
            cls,
            measure_name: str,
            run_dicts: [dict],
            command_base: str,
            out_file_path: str,
            no_title: bool,
            log_x: bool,
            log_y: bool,
            rotate_x: bool,
            include_ci: bool | None,
    ):
        x_names = [run_dict['x_name'] for run_dict in run_dicts]
        x_name = x_names[0]

        assert all(x == x_name for x in x_names)

        x_values = [run_dict['x'] for run_dict in run_dicts]
        x_all_numeric = all(cls._is_float(x) for x in x_values)

        if x_all_numeric:
            x_values = [float(x) for x in x_values]

        if include_ci is None:
            min_measures = min(run_dict['measures'][measure_name]['stats']['cnt'] for run_dict in run_dicts)
            include_ci = min_measures >= default.RUNS

        lineplot_dict = {x_name: [], 'avg': [], 'ci_05': [], 'ci_95': []}
        scatterplot_dict = {'x': [], 'y': []}

        for x_value, run_dict in zip(x_values, run_dicts):

            stats_dict = run_dict['measures'][measure_name]['stats']
            data_list  = run_dict['measures'][measure_name]['data']

            lineplot_dict[x_name].append(x_value)
            lineplot_dict['avg'].append(stats_dict['avg'])

            if include_ci:
                ci_05 = stats_dict['avg'] - 1.96 * stats_dict['std'] / stats_dict['cnt'] ** 0.5
                ci_95 = stats_dict['avg'] + 1.96 * stats_dict['std'] / stats_dict['cnt'] ** 0.5

                lineplot_dict['ci_05'].append(ci_05)
                lineplot_dict['ci_95'].append(ci_95)

            scatterplot_dict['x'] += [x_value] * len(data_list)
            scatterplot_dict['y'] += data_list

        fig, ax = plt.subplots()

        sns.scatterplot(scatterplot_dict, x='x', y='y', marker='o', color='black', alpha=0.15, edgecolor=None)

        if include_ci:
            sns.lineplot(lineplot_dict, x=x_name, y='ci_95', linestyle='--', color='gray', label='ci_95')
            sns.lineplot(lineplot_dict, x=x_name, y='ci_05', linestyle='--', color='gray', label='ci_05')

        # doing this to remove the white edge around lineplot points
        sns.lineplot   (lineplot_dict, x=x_name, y='avg', linestyle='-', color='red', label='avg')
        sns.scatterplot(lineplot_dict, x=x_name, y='avg', marker='o',    color='red', edgecolor=None)

        if log_x: ax.set_xscale('log')
        if log_y: ax.set_yscale('log')

        # reorder the legend
        if include_ci:
            (h_95, h_05, h_avg), (l_95, l_05, l_avg) = ax.get_legend_handles_labels()
            handles, labels = [h_95, h_avg, h_05], [l_95, l_avg, l_05]
            ax.legend(handles=handles, labels=labels)

        if not no_title:
            ax.set_title(command_base, fontsize=10)
            # ax.set_title(command_base, fontsize=10, font='Courier New')

        ax.set_xticks(x_values)
        ax.set_xlabel(x_name)
        ax.set_ylabel(measure_name)
        ax.grid(True, alpha=0.5, axis="y", linestyle="--")

        if rotate_x:
            fig.autofmt_xdate()

        plt.tight_layout()

        # get info for debug:
        # left, right = ax.get_xlim()
        # bottom, top = ax.get_ylim()
        #
        # # Print the values
        # print(f"Left: {left}, Right: {right}, Bottom: {bottom}, Top: {top}")
        #
        # # plt.subplots_adjust(left=0.1, right=0.9, bottom=0.1, top=0.9)

        fig.savefig(out_file_path)
        plt.close(fig)

    @classmethod
    def _is_float(cls, num: str) -> bool:
        try:
            float(num)
            return True
        except ValueError:
            return False

    @classmethod
    def render_histogram(cls, measure_name: str, run_dicts: [dict], out_file_path: str, skip_rug: bool):
        cls._render('hist', measure_name=measure_name, run_dicts=run_dicts, out_file_path=out_file_path, skip_rug=skip_rug)

    @classmethod
    def render_kernel_density_estimate(cls, measure_name: str, run_dicts: [dict], out_file_path: str, skip_rug):
        cls._render('kde', measure_name=measure_name, run_dicts=run_dicts, out_file_path=out_file_path, skip_rug=skip_rug)

    @classmethod
    def render_stacked_hist_kde(cls, measure_name: str, run_dicts: [dict], out_file_path: str, skip_rug: bool):
        cls._render('stacked', measure_name=measure_name, run_dicts=run_dicts, out_file_path=out_file_path, skip_rug=skip_rug)

    @classmethod
    def _render(cls, plot_type: str, measure_name: str, run_dicts: [dict], out_file_path: str, skip_rug: bool):
        assert plot_type in ['hist', 'kde', 'stacked']

        x_values = [run_dict['x'] for run_dict in run_dicts]
        measures_dict = {run_dict['x']: run_dict['measures'][measure_name]['data'] for run_dict in run_dicts}

        n = len(run_dicts)
        palette = sns.color_palette('tab10', n_colors=n)

        n_graphs = 2 if (plot_type == 'stacked') else 1
        n_rugs   = 0 if skip_rug else n
        n_rows   = n_graphs + n_rugs
        fig, axs = plt.subplots(nrows=n_rows, sharex=True, gridspec_kw={'hspace': 0, 'height_ratios': [10+n] * n_graphs + [1] * n_rugs})
        if n_rows == 1:
            axs = [axs]

        if plot_type == 'hist':
            sns.histplot(data=measures_dict, hue_order=x_values, fill=True, ax=axs[0])
        if plot_type == 'kde':
            sns.kdeplot (data=measures_dict, hue_order=x_values, fill=True, ax=axs[0])
        if plot_type == 'stacked':
            sns.histplot(data=measures_dict, hue_order=x_values, fill=True, ax=axs[0])
            sns.kdeplot (data=measures_dict, hue_order=x_values, fill=True, ax=axs[1])
            axs[1].legend([],[], frameon=False)  # remove legend for second plot, otherwise it would repeat

        for ax in axs[:n_graphs]:
            ax.set_xlabel(measure_name)
            ax.grid(True, alpha=0.5, axis="y", linestyle="--")

        for x_value, measures, color, ax in zip(measures_dict.keys(), measures_dict.values(), palette, axs[n_graphs:]):
            sns.rugplot(data={x_value: measures}, x=x_value, height=0.75, color=color, ax=ax)
            ax.set_xlabel(measure_name)
            ax.set_yticks([])         # hide y ticks
            ax.set_facecolor('none')  # make transparent to see all x ticks

        plt.tight_layout()

        fig.savefig(out_file_path)
        plt.close(fig)
