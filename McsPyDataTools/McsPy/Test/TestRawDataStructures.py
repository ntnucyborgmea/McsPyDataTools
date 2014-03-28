import unittest
import McsData
import datetime
import exceptions
import numpy as np

from McsPy import *

test_raw_frame_data_file_path = ".\\TestData\\Sensors-10x100ms-10kHz.h5"

test_data_file_path = ".\\TestData\\2014-02-27T08-30-03W8SpikeCutoutsAndTimestampsAndRawData.h5"

#@unittest.skip("showing the principle structure of python unit tests")
#class Test_TestRawDataStructures(unittest.TestCase):
#    def test_A(self):
#        self.fail("Not implemented")

class Test_RawData(unittest.TestCase):
    def setUp(self):
        self.data = McsData.RawData(test_data_file_path)
        self.raw_frame_data = McsData.RawData(test_raw_frame_data_file_path)

class Test_RawDataContainer(Test_RawData):
    # Test MCS-HDF5 version
    def test_mcs_hdf5_version(self):
        self.assertEqual(self.data.mcs_hdf5_protocol_type, McsHdf5Protocols.RAW_DATA[0], 
                         "The MCS-HDF5 protocol type was '%s' and not '%s' as expected!" % (self.data.mcs_hdf5_protocol_type, McsHdf5Protocols.RAW_DATA[0]))
        self.assertEqual(self.data.mcs_hdf5_protocol_type_version, 1, 
                         "The MCS-HDF5 protocol version was '%s' and not '1' as expected!" % self.data.mcs_hdf5_protocol_type_version)

    def test_mcs_hdf5_version_frame(self):
        self.assertEqual(self.data.mcs_hdf5_protocol_type, McsHdf5Protocols.RAW_DATA[0], 
                         "The MCS-HDF5 protocol type was '%s' and not '%s' as expected!" % (self.data.mcs_hdf5_protocol_type, McsHdf5Protocols.RAW_DATA[0]))
        self.assertEqual(self.data.mcs_hdf5_protocol_type_version, 1, 
                         "The MCS-HDF5 protocol version was '%s' and not '1' as expected!" % self.data.mcs_hdf5_protocol_type_version)

    # Test session:
    def test_session_attributes(self):
        self.assertEqual(self.data.comment, '', 'Comment is different!')
        self.assertEqual(self.data.clr_date, 'Donnerstag, 27. Februar 2014', 'Clr-Date is different!')
        self.assertEqual(self.data.date_in_clr_ticks, 635290866032185769, 'Clr-Date-Ticks are different!')
        self.assertEqual(self.data.date, datetime.datetime(2014,2,27), 'Date is different!');
        self.assertEqual(str(self.data.file_guid), '3be1f837-7374-4600-9f69-c86bcee5ef41', 'FileGUID is different!')
        self.assertEqual(str(self.data.mea_layout), 'Linear8', 'Mea-Layout is different!')
        self.assertEqual(self.data.mea_sn, '', 'MeaSN is different!')
        self.assertEqual(self.data.mea_name, 'Linear8', 'MeaName is different!')
        self.assertEqual(self.data.program_name, 'Multi Channel Experimenter', 'Program name is different!')
        self.assertEqual(self.data.program_version, '0.8.6.0', 'Program version is different!') 


    # Test recording:
    def test_count_recordings(self):
        self.assertEqual(len(self.data.recordings), 1, 'There should be only one recording!')

    def test_recording_attributes(self):
        first_recording = self.data.recordings[0]
        self.assertEqual(first_recording.comment, '', 'Recording comment is different!')
        self.assertEqual(first_recording.duration, 7900000, 'Recording duration is different!')
        self.assertEqual(first_recording.label, '', 'Recording label is different!')
        self.assertEqual(first_recording.recording_id, 0, 'Recording ID is different!')
        self.assertEqual(first_recording.recording_type, '', 'Recording type is different!')
        self.assertEqual(first_recording.timestamp, 0, 'Recording time stamp is different!')
        self.assertAlmostEqual(first_recording.duration_time.to(ureg.sec).magnitude, 7.9, places = 1, msg = 'Recording time stamp is different!')

    # Test analog streams:
    def test_count_analog_streams(self):
         self.assertEqual(len(self.data.recordings[0].analog_streams), 1, 'There should be only one analog stream inside the recording!')

    def test_analog_stream_attributes(self):
        first_analog_stream = self.data.recordings[0].analog_streams[0]
        self.assertEqual(first_analog_stream.data_subtype, 'Electrode', 'Analog stream data sub type is different!')
        self.assertEqual(first_analog_stream.label, '', 'Analog stream label is different!')
        self.assertEqual(str(first_analog_stream.source_stream_guid), '00000000-0000-0000-0000-000000000000', 'Analog stream source GUID is different!')
        self.assertEqual(str(first_analog_stream.stream_guid), '3a1054d5-2c9f-4ddf-877b-282b86c1d5ab', 'Analog stream GUID is different!')
        self.assertEqual(first_analog_stream.stream_type, 'Analog', 'Analog stream type is different!')
    
    def test_analog_stream(self):
        data_set = self.data.recordings[0].analog_streams[0].channel_data
        self.assertEqual(data_set.shape, (8, 158024), 'Shape of dataset is different!')
        
        time_stamp_index = self.data.recordings[0].analog_streams[0].time_stamp_index
        self.assertEqual(time_stamp_index.shape, (1, 3), 'Shape of time stamp index is different!')

        channel_infos =  self.data.recordings[0].analog_streams[0].channel_infos
        self.assertEqual(len(channel_infos), 8, 'Number of channel info objects is different!')
        self.assertEqual(len(channel_infos[0].info), 16, 'Number of of components of an channel info object is different!')

    def test_analog_stream_data(self):
        analog_stream =  self.data.recordings[0].analog_streams[0]
        signal = analog_stream.get_channel_in_range(0, 48407, 48422)
        sig = signal[0]
        scale = 381469 * 10**-9
        expected_sig = np.array([-13, -17, -12, -17, -23, -24, -13, -10, -14, -16, -10, -18, -25, -20, -20, -15], dtype=np.float) * scale
        np.testing.assert_almost_equal(sig, expected_sig, decimal = 5)
        #self.assertEquals(map(lambda x: x, sig), expected_sig, "Signal values were '%s' and not as expected '%s'" % (sig, expected_sig))
        self.assertEqual(str(signal[1]), 'volt', "Unit of sampled values was expected to be 'volt' but was '%s'!" % str(signal[1]))

    def test_analog_stream_data_timestamps(self):
        analog_stream =  self.data.recordings[0].analog_streams[0]
        signal_ts = analog_stream.get_channel_sample_timestamps(6, 19965, 19970)
        sig_ts = signal_ts[0]
        expected_ts = [998250, 998300, 998350, 998400, 998450, 998500]
        self.assertEquals(map(lambda x: x, sig_ts), expected_ts, "Selected time stamps were '%s' and not as expected '%s'" % (sig_ts, expected_ts))
        self.assertEqual(str(signal_ts[1]), 'microsecond', "Unit of time stamps was expected to be 'microsecond' but was '%s'!" % str(signal_ts[1]))

    # Test frame streams:
    def test_count_frame_streams(self):
         self.assertEqual(len(self.raw_frame_data.recordings[0].frame_streams), 1, 'There should be only one frame stream!')
         self.assertEqual(len(self.raw_frame_data.recordings[0].frame_streams[0].frame_entity), 1, 'There should be only one frame entity inside the stream!')

    def test_frame_stream_attributes(self):
        first_frame_stream = self.raw_frame_data.recordings[0].frame_streams[0]
        self.assertEqual(first_frame_stream.data_subtype, 'Unknown', 'Frame stream data sub type is different!')
        self.assertEqual(first_frame_stream.label, '', 'Frame stream label is different!')
        self.assertEqual(str(first_frame_stream.source_stream_guid), '11bee63c-8714-4b2b-8cf9-228b1915f183', 'Frame stream source GUID is different!')
        self.assertEqual(str(first_frame_stream.stream_guid), '784bf2ba-0e1b-4f3a-acc6-825af9bd1bf1', 'Frame stream GUID is different!')
        self.assertEqual(first_frame_stream.stream_type, 'Frame', 'Frame stream type is different!')
    
    def test_frame_infos(self):
        conv_fact_expected = np.zeros(shape=(65,65), dtype=np.int32) + 1000
        info_expected = {
                     'FrameLeft': 1, 'Exponent': -9, 'RawDataType': 'Short', 'LowPassFilterCutOffFrequency': '-1', 'Label': 'ROI 1', 
                     'FrameTop': 1, 'ADZero': 0, 'LowPassFilterOrder': -1, 'ReferenceFrameTop': 1, 'FrameRight': 65, 'HighPassFilterType': '', 
                     'Tick': 50, 'SensorSpacing': 1, 'HighPassFilterCutOffFrequency': '-1', 'FrameDataID': 0, 'FrameID': 1, 'GroupID': 1, 
                     'ReferenceFrameRight': 65, 'ReferenceFrameBottom': 65, 'LowPassFilterType': '', 'HighPassFilterOrder': -1, 
                     'ReferenceFrameLeft': 1, 'FrameBottom': 65, 'Unit': 'V'
        }
        frame_info =  self.raw_frame_data.recordings[0].frame_streams[0].frame_entity[1].info
        self.assertEqual(len(frame_info.info), 24, 'Number of of components of an channel info object is different!')
        info_key_diff = set(frame_info.info.keys()) - set(info_expected.keys())
        if not info_key_diff:
            for key, value in frame_info.info.items():
                self.assertEqual(
                    value, info_expected[key], 
                    "Frame info object for key '%(k)s' is ('%(val)s') not as expected ('%(ex_val)s')!" % {'k':key, 'val':value, 'ex_val':info_expected[key]}
                )
        self.assertEqual(frame_info.frame.height, 65, "Frame height was '%s' and not '65' as expected!" % frame_info.frame.height)
        self.assertEqual(frame_info.frame.width, 65, "Frame width was '%s' and not '65' as expected!" % frame_info.frame.width)
        self.assertEqual(frame_info.reference_frame.height, 65, "Frame height was '%s' and not '65' as expected!" % frame_info.reference_frame.height)
        self.assertEqual(frame_info.reference_frame.width, 65, "Frame width was '%s' and not '65' as expected!" % frame_info.reference_frame.width)
        self.assertEqual(frame_info.adc_basic_step.magnitude, 10**-9, "ADC step was '%s' and not '10^-9 V' as expected!" % frame_info.adc_basic_step)
        self.assertEqual(frame_info.adc_step_for_sensor(0,0).magnitude, 1000 * 10**-9, "ADC step was '%s' and not '1000 * 10^-9 V' as expected!" % frame_info.adc_step_for_sensor(0,0))
        self.assertEqual(frame_info.adc_step_for_sensor(1,1).magnitude, 1000 * 10**-9, "ADC step was '%s' and not '1000 * 10^-9 V' as expected!" % frame_info.adc_step_for_sensor(1,1))
        self.assertEqual(frame_info.adc_step_for_sensor(63,63).magnitude, 1000 * 10**-9, "ADC step was '%s' and not '1000 * 10^-9 V' as expected!" % frame_info.adc_step_for_sensor(63,63))
        self.assertTrue((frame_info.conversion_factors == conv_fact_expected).all(), "Frame sensor conversion factors matrix is different from the expected one!")
        self.assertRaises(exceptions.IndexError, frame_info.adc_step_for_sensor, 65,65)          

    def test_frame_data(self):
        frame_entity =  self.raw_frame_data.recordings[0].frame_streams[0].frame_entity[1]
        frame_data = frame_entity.data
        frame = frame_data[:,:,1]
        self.assertEqual(frame.shape, (65,65), "Second slice was '%s' and not '(65,65)' as expected!" % str(frame.shape))
        selected_values = [frame[0,0], frame[9,3], frame[0,5]]
        expected_values = [    -10000,        211,       -727]
        self.assertEquals(selected_values, expected_values, "Selected ADC values were '%s' and not as expected '%s'" % (selected_values, expected_values))
        sensor_signal = frame_entity.get_sensor_signal(30, 30, 0, 1000)
        sig = sensor_signal[0]
        self.assertEquals(len(sig), 1001, "Length of sensor signal was '%s' and not as expected '1001'" % len(sig))

    def test_frame_data_timestamps(self):
        frame_entity =  self.raw_frame_data.recordings[0].frame_streams[0].frame_entity[1]
        time_stamps = frame_entity.get_frame_timestamps(0,2000)
        ts = time_stamps[0]
        self.assertEqual(len(ts), 2001, "Number of time stamps were '%s' and not as expected '2001'" % len(ts))
        time_stamps = frame_entity.get_frame_timestamps(1995,2005)
        ts = time_stamps[0]
        self.assertEqual(len(ts), 11, "Number of time stamps were '%s' and not as expected '11'" % len(ts))
        expected_ts = [199750, 199800, 199850, 199900, 199950, 200000,  1000000,  1000050,  1000100, 1000150, 1000200]
        self.assertEquals(map(lambda x: x, ts), expected_ts, "Time stamps were '%s' and not as expected '%s'" % (ts, expected_ts))
        time_stamps = frame_entity.get_frame_timestamps(0,5000)
        ts = time_stamps[0]
        self.assertEqual(len(ts), 5001, "Number of time stamps were '%s' and not as expected '5001'" % len(ts))
        selected_ts = [ ts[0], ts[1], ts[2000], ts[2001], ts[2002], ts[4001], ts[4002], ts[4003]]
        expected_ts = [100000,100050,   200000,  1000000,  1000050,  1100000,  3000000,  3000050]
        self.assertEquals(selected_ts, expected_ts, "Selected time stamps were '%s' and not as expected '%s'" % (selected_ts, expected_ts))
        time_stamps = frame_entity.get_frame_timestamps(16008,16008)
        ts = time_stamps[0]
        self.assertEqual(len(ts), 1, "Number of time stamps were '%s' and not as expected '1'" % len(ts))
        self.assertEquals(ts[0], 12500000, "Time stamps were '%s' and not as expected '%s'" % (ts, expected_ts))
        self.assertEqual(str(time_stamps[1]), 'microsecond', "Unit of time stamps was expected to be 'microsecond' but was '%s'!" % str(time_stamps[1]))

    # Test event streams:
    def test_count_event_streams(self):
        self.assertEqual(len(self.data.recordings[0].event_streams), 1, 'There should be only one event stream inside the recording!')
        self.assertEqual(len(self.data.recordings[0].event_streams[0].event_entity), 8, 'There should be 8 event entities inside the stream!')

    def test_event_stream_attributes(self):
        first_event_stream = self.data.recordings[0].event_streams[0]
        self.assertEqual(first_event_stream.data_subtype, 'SpikeTimeStamp', 'Event stream data sub type is different from expected \'SpikeTimeStamp\'!')
        self.assertEqual(first_event_stream.label, '', 'Event stream label is different!')
        self.assertEqual(str(first_event_stream.source_stream_guid), '3a1054d5-2c9f-4ddf-877b-282b86c1d5ab', 'Event stream source GUID is different!')
        self.assertEqual(str(first_event_stream.stream_guid), '5a12d97b-f119-4ed6-aab7-5ab57a6f9f41', 'Event stream GUID is different!')
        self.assertEqual(first_event_stream.stream_type, 'Event', 'Event stream type is different!')

    def test_event_infos(self):
        first_event_entity = self.data.recordings[0].event_streams[0].event_entity[0]
        self.assertEqual(first_event_entity.info.id, 0, "ID is not as expected!")
        self.assertEqual(first_event_entity.info.raw_data_bytes, 4, "RawDataBytes is not as expected!")
        self.assertEquals(first_event_entity.info.source_channel_ids, [0],"Source channel IDs are different!") 
        self.assertEquals(first_event_entity.info.source_channel_labels.values(), 
                          ["E1"],"Source channels label is different (was '%s' instead of '['E1']')!" % 
                          first_event_entity.info.source_channel_labels.values()) 

    def test_event_data(self):
        first_event_entity = self.data.recordings[0].event_streams[0].event_entity[0]
        self.assertEqual(first_event_entity.count, 36, "Count was expected to be 36 but was %s!" % first_event_entity.count)
        events = first_event_entity.get_events()
        self.assertEqual(str(events[1]), 'microsecond', "Event time unit was expected to be 'microsecond' but was '%s'!" % str(events[1]))
        self.assertEqual((events[0]).shape, (2,36), "Event structured was expected to be (2,36) but was %s!" % str(events[0].shape))
        events_ts = first_event_entity.get_event_timestamps(0,3)
        #self.assertAlmostEquals(events[0],[1.204050, 2.099150, 2.106800] , places = 5, msg = "Event time stamps were not as expected!")
        np.testing.assert_almost_equal(events_ts[0],[1204050, 2099150, 2106800], decimal = 5)
        events_ts = first_event_entity.get_event_timestamps(35,36)
        self.assertAlmostEqual(events_ts[0][0], 7491100, places = 4, msg = "Last event time stamp was %s and not as expected 7491100!" % events[0][0])
        events_duration = first_event_entity.get_event_durations(15,22)
        np.testing.assert_almost_equal(events_duration[0],[0, 0, 0, 0, 0, 0, 0], decimal = 5)
        self.assertRaises(exceptions.IndexError, first_event_entity.get_events, 16, 4)
        self.assertRaises(exceptions.IndexError, first_event_entity.get_events, 412, 500)   
        self.assertRaises(exceptions.IndexError, first_event_entity.get_events, -1, 5) 

    # Test segment streams:
    def test_count_segment_streams(self):
        self.assertEqual(len(self.data.recordings[0].segment_streams), 1, 'There should be only one segment stream inside the recording!')
        self.assertEqual(len(self.data.recordings[0].segment_streams[0].segment_entity), 8, 'There should be 8 segment entities inside the stream!')

    def test_segment_stream_attributes(self):
        first_segment_stream = self.data.recordings[0].segment_streams[0]
        self.assertEqual(first_segment_stream.stream_type, 'Segment', "Segment stream type was '%s' and not 'Segment'!" % first_segment_stream.stream_type)
        self.assertEqual(first_segment_stream.data_subtype, 'Spike', "Segment stream data sub type was '%s' and not 'Spike' as expected!" % first_segment_stream.data_subtype)
        self.assertEqual(first_segment_stream.label, '', "Segment label was '%s' and not '' as expected!" % first_segment_stream.label)
        self.assertEqual(str(first_segment_stream.source_stream_guid), '3a1054d5-2c9f-4ddf-877b-282b86c1d5ab', 
                         "Segment stream source GUID was '%s' and not '3a1054d5-2c9f-4ddf-877b-282b86c1d5ab' as expected!" % str(first_segment_stream.source_stream_guid))
        self.assertEqual(str(first_segment_stream.stream_guid), '45a5873f-963a-4a48-a18e-2a9b0ff69005', 
                         "Segment stream GUID was '%s' and not '45a5873f-963a-4a48-a18e-2a9b0ff69005' as expected!" % str(first_segment_stream.stream_guid))

    def test_segment_infos(self):
        fifth_segment_entity = self.data.recordings[0].segment_streams[0].segment_entity[4]
        self.assertEqual(fifth_segment_entity.info.id, 4, "ID was '%s' and not '4' as expected!" % fifth_segment_entity.info.id)
        self.assertEqual(fifth_segment_entity.info.group_id, 0, "Group ID was '%s' and not '0' as expected!" % fifth_segment_entity.info.group_id)
        self.assertEqual(fifth_segment_entity.info.pre_interval.magnitude, 1000, "Pre-Interval was '%s' and not '1000' as expected!" % fifth_segment_entity.info.pre_interval.magnitude)
        self.assertEqual(str(fifth_segment_entity.info.pre_interval.units), 'microsecond', "Pre-Interval unit was '%s' and not 'microsecond' as expected!" % str(fifth_segment_entity.info.pre_interval.units))
        self.assertEqual(fifth_segment_entity.info.post_interval.magnitude, 2000, "Post-Interval was '%s' and not '2000' as expected!" % fifth_segment_entity.info.post_interval.magnitude)
        self.assertEqual(str(fifth_segment_entity.info.post_interval.units), 'microsecond', "Post-Interval unit was '%s' and not 'microsecond' as expected!" % str(fifth_segment_entity.info.post_interval.units))
        self.assertEqual(fifth_segment_entity.info.type, 'Cutout', "Type was '%s' and not 'Cutout' as expected!" % fifth_segment_entity.info.type)
        self.assertEqual(fifth_segment_entity.info.count, 1, "Count of segments was '%s' and not '1' as expected!" % fifth_segment_entity.info.count)
        self.assertEquals(fifth_segment_entity.info.source_channel_of_segment.keys(), [0], 
                          "Source channel dataset index was different (was '%s' instead of '['0']')!" % fifth_segment_entity.info.source_channel_of_segment.keys()) 
        self.assertEquals(fifth_segment_entity.info.source_channel_of_segment[0].channel_id, 4, 
                          "Source channel ID was different (was '%s' instead of '4')!" % fifth_segment_entity.info.source_channel_of_segment[0].channel_id) 

    def test_segment_data(self):
        first_segment_entity = self.data.recordings[0].segment_streams[0].segment_entity[0]
        self.assertEqual(first_segment_entity.segment_sample_count, 36, "Segment sample count was expected to be  but was %s!" % first_segment_entity.segment_sample_count)
        signal = first_segment_entity.get_segment_in_range(0)
        self.assertEqual(signal[0].shape, (61, 36), "Matrix of segment signal points was expected to be '(61,36)' but was '%s'!" % str(signal[0].shape))
        self.assertEqual(str(signal[1]), 'volt', "Unit of segment signal was expected to be 'volt' but was '%s'!" % str(signal[1]))
        signal_flat = first_segment_entity.get_segment_in_range(0, flat = True)
        self.assertEqual(len(signal_flat[0]), 2196, "Vector ('flat = True') of segment signal points was expected to be '2196' but was '%s'!" % len(signal_flat[0]))
        self.assertRaises(exceptions.IndexError, first_segment_entity.get_segment_in_range, segment_id = 0, flat = False, idx_start = 16, idx_end = 4)
        self.assertRaises(exceptions.IndexError, first_segment_entity.get_segment_in_range, segment_id = 0, flat = False, idx_start = 40, idx_end = 49)
        self.assertRaises(exceptions.IndexError, first_segment_entity.get_segment_in_range, segment_id = 0, flat = False, idx_start = -1, idx_end = 10)

    def test_segment_data_timestamps(self):
        first_segment_entity = self.data.recordings[0].segment_streams[0].segment_entity[0]
        signal_ts = first_segment_entity.get_segment_sample_timestamps(0)
        self.assertEqual(signal_ts[0].shape, (61, 36), "Matrix of segment time stamps was expected to be '(61,36)' but was '%s'!" % str(signal_ts[0].shape))
        self.assertEqual(str(signal_ts[1]), 'microsecond', "Unit of time stamps was expected to be 'microsecond' but was '%s'!" % str(signal_ts[1]))
        ts_selected = (signal_ts[0][:,0]).tolist()
        expected_ts_first_segment = [1203050, 1203100, 1203150, 1203200, 1203250, 1203300, 1203350, 
                                    1203400, 1203450, 1203500, 1203550, 1203600, 1203650, 1203700, 
                                    1203750, 1203800, 1203850, 1203900, 1203950, 1204000, 1204050, 
                                    1204100, 1204150, 1204200, 1204250, 1204300, 1204350, 1204400, 
                                    1204450, 1204500, 1204550, 1204600, 1204650, 1204700, 1204750, 
                                    1204800, 1204850, 1204900, 1204950, 1205000, 1205050, 1205100, 
                                    1205150, 1205200, 1205250, 1205300, 1205350, 1205400, 1205450, 
                                    1205500, 1205550, 1205600, 1205650, 1205700, 1205750, 1205800, 
                                    1205850, 1205900, 1205950, 1206000, 1206050]
        self.assertEquals(ts_selected, expected_ts_first_segment, "Time stamps for the first segment were '%s' and not as expected '%s" % (ts_selected, expected_ts_first_segment))
        ts_selected = (signal_ts[0][:,2]).tolist()
        expected_ts_third_segment = [2105800, 2105850, 2105900, 2105950, 2106000, 2106050, 2106100, 
                                    2106150, 2106200, 2106250, 2106300, 2106350, 2106400, 2106450, 
                                    2106500, 2106550, 2106600, 2106650, 2106700, 2106750, 2106800, 
                                    2106850, 2106900, 2106950, 2107000, 2107050, 2107100, 2107150, 
                                    2107200, 2107250, 2107300, 2107350, 2107400, 2107450, 2107500, 
                                    2107550, 2107600, 2107650, 2107700, 2107750, 2107800, 2107850, 
                                    2107900, 2107950, 2108000, 2108050, 2108100, 2108150, 2108200, 
                                    2108250, 2108300, 2108350, 2108400, 2108450, 2108500, 2108550, 
                                    2108600, 2108650, 2108700, 2108750, 2108800]
        self.assertEquals(ts_selected, expected_ts_third_segment, "Time stamps for the third segment were '%s' and not as expected '%s" % (ts_selected, expected_ts_third_segment))
        signal_flat_ts = first_segment_entity.get_segment_sample_timestamps(0, flat = True)
        self.assertEqual(len(signal_flat_ts[0]), 2196, "Vector ('flat = True') of segment signal points was expected to be '2196' but was '%s'!" % len(signal_flat_ts[0]))
        self.assertRaises(exceptions.IndexError, first_segment_entity.get_segment_sample_timestamps, segment_id = 0, flat = False, idx_start = 16, idx_end = 4)
        self.assertRaises(exceptions.IndexError, first_segment_entity.get_segment_sample_timestamps, segment_id = 0, flat = False, idx_start = 40, idx_end = 49)
        self.assertRaises(exceptions.IndexError, first_segment_entity.get_segment_sample_timestamps, segment_id = 0, flat = False, idx_start = -1, idx_end = 10)

if __name__ == '__main__':
    unittest.main()