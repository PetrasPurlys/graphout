from dataclasses import dataclass


@dataclass
class ProcessLifetime:
    skip:             bool
    measurement_name: str


@dataclass
class NumericResults:
    no_output:   bool
    file_name:   str
    folder_name: str
    no_raw_data: bool


@dataclass
class GraphicResults:
    no_output:      bool
    no_conf_int:    bool
    force_conf_int: bool
    no_hist:        bool
    no_kde:         bool
    no_rug:         bool
    create_stacked_hist_kde: bool
    no_title:       bool
    log_x_axis:     bool
    log_y_axis:     bool
    rotate_x:       bool

    def get_include_ci(self) -> bool | None:
        if self.force_conf_int:
            return True
        elif self.no_conf_int:
            return False
        else:
            return None


@dataclass
class Parameters:
    command_template:        str
    command_template_args_1: []    # only 1d case currently supported
    number_of_runs:          int
    capture_patterns:        [str]
    stream:                  str
    parallel_process_count:  int
    quiet:                   bool
    print_progress:          bool
    print_summary:           bool

    numeric_results:  NumericResults
    graphic_results:  GraphicResults
    process_lifetime: ProcessLifetime

    def __post_init__(self):
        if not self.process_lifetime.skip:
            measure_name_list_user_only = self._get_measure_name_list_user_only()
            name = self.process_lifetime.measurement_name
            if name in measure_name_list_user_only:
                print(f'One of the capture tags / regexes matches the process lifetime measure name = {name}, '
                      f'either change it or set skip=True')
                exit(1)

    def get_pattern_dict(self) -> dict:
        return {x.split(':')[0]: x.split(':')[1] for x in self.capture_patterns}

    def get_measure_name_list(self) -> [str]:
        measure_name_list = self._get_measure_name_list_user_only()
        if not self.process_lifetime.skip:
            measure_name_list.append(self.process_lifetime.measurement_name)
        return measure_name_list

    def _get_measure_name_list_user_only(self) -> [str]:
        return list(self.get_pattern_dict().keys())
