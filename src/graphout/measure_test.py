from graphout.measure import Measure
from graphout.test.test import Test


class MeasureTest(Test):

    @classmethod
    def setUpClass(cls) -> None:
        cls.run_dict_list = Measure.run(
            command_template='ping www.example.com -l [payload_bytes]',
            command_template_args_1=['1', '100', '200'],
            number_of_runs=5,
            stream='out',
            pattern_dict={'ping_time': 'time=([0-9]*)ms'},
            proc_count=1,
            quiet=True,
            print_progress=False,
            no_raw_data=False,
            no_proc_time=False,
            measure_proc_time_name='proc_lifetime_s',
        )

    def test_command_is_correct(self):
        self.assertTrue(self.run_dict_list[0]['command'] == 'ping www.example.com -l 1')
        self.assertTrue(self.run_dict_list[1]['command'] == 'ping www.example.com -l 100')
        self.assertTrue(self.run_dict_list[2]['command'] == 'ping www.example.com -l 200')

    def test_measure_list_contains_proc_time_and_ping_time(self):
        self.assertTrue('proc_lifetime_s' in self.run_dict_list[0]['measures'])
        self.assertTrue('ping_time'       in self.run_dict_list[0]['measures'])

    def test_ping_value_count_is_20(self):
        self.assertTrue(len(self.run_dict_list[0]['measures']['ping_time']['data']) == 20)
