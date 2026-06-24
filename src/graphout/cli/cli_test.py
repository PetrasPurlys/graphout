from graphout import default
from graphout.cli.cli import CLI
from graphout.cli.parameters import (GraphicResults, NumericResults,
                                     Parameters, ProcessLifetime)
from graphout.test.test import Test


class CliTest(Test):

    @classmethod
    def setUpClass(cls) -> None:
        cls.args_1 = "--patterns ping_time:time=([0-9]*)ms -n 5 --proc 2 -q -- ping www.example.com -l {x} -- 100 200 300".split(' ')
        cls.prm_1_exp = Parameters(
            command_template='ping www.example.com -l {x}',
            command_template_args_1=['100', '200', '300'],
            number_of_runs=5,
            capture_patterns=['ping_time:time=([0-9]*)ms'],
            stream=default.STD_STREAM,
            parallel_process_count=2,
            quiet=True,
            print_progress=True,
            print_summary=True,
            numeric_results=NumericResults(
                no_output=False,
                file_name=default.RESULT_FILE_NAME,
                folder_name='',
                no_raw_data=False,
            ),
            graphic_results=GraphicResults(
                no_output=False,
                no_conf_int=False,
                force_conf_int=False,
                no_hist=False,
                no_kde=False,
                no_rug=False,
                create_stacked_hist_kde=False,
                no_title=False,
                log_x_axis=False,
                log_y_axis=False,
                rotate_x=False,
            ),
            process_lifetime=ProcessLifetime(
                skip=True,
                measurement_name='',
            ),
        )

    def test_parameters_are_parsed_correctly(self):
        prm_1_act = CLI.parse_args_to_parameters(self.args_1)
        self.assertEqual(self.prm_1_exp, prm_1_act)
