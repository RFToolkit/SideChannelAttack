#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: nRF24L01(+)-receiver
# Author: kittennbfive
# Copyright: AGPLv3+
# Description: simple receiver for nRF24L01(+) and similar
# GNU Radio version: 3.9.8.0

from distutils.version import StrictVersion

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print("Warning: failed to XInitThreads()")

from PyQt5 import Qt
from PyQt5.QtCore import QObject, pyqtSlot
from gnuradio import eng_notation
from gnuradio import qtgui
from gnuradio.filter import firdes
import sip
from gnuradio import analog
import math
from gnuradio import blocks
from gnuradio import filter
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio.qtgui import Range, RangeWidget
from PyQt5 import QtCore
import osmosdr
import time



from gnuradio import qtgui

class nrf_receiver(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "nRF24L01(+)-receiver", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("nRF24L01(+)-receiver")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except:
            pass
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "nrf_receiver")

        try:
            if StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
                self.restoreGeometry(self.settings.value("geometry").toByteArray())
            else:
                self.restoreGeometry(self.settings.value("geometry"))
        except:
            pass

        ##################################################
        # Variables
        ##################################################
        self.nrf_speed = nrf_speed = 2
        self.nrf_channel = nrf_channel = 2
        self.write_output = write_output = 0
        self.trig_level = trig_level = 0.25
        self.thre_low = thre_low = -0.2
        self.thre_high = thre_high = 0.2
        self.scope_nb_points = scope_nb_points = (1024, 4096, 8192)[nrf_speed]
        self.samples_per_bit = samples_per_bit = (6,6,8)[nrf_speed]
        self.samp_rate = samp_rate = (12e6, 6e6, 2e6)[nrf_speed]
        self.lpf_tran_width = lpf_tran_width = (800e3,300e3,250e3)[nrf_speed]
        self.lpf_cutoff = lpf_cutoff = (1800e3, 900e3, 700e3)[nrf_speed]
        self.frequency = frequency = 2.4E9+nrf_channel*1e6
        self.demod_gain = demod_gain = 1

        ##################################################
        # Blocks
        ##################################################
        _write_output_check_box = Qt.QCheckBox("Write to file/pipe")
        self._write_output_choices = {True: 1, False: 0}
        self._write_output_choices_inv = dict((v,k) for k,v in self._write_output_choices.items())
        self._write_output_callback = lambda i: Qt.QMetaObject.invokeMethod(_write_output_check_box, "setChecked", Qt.Q_ARG("bool", self._write_output_choices_inv[i]))
        self._write_output_callback(self.write_output)
        _write_output_check_box.stateChanged.connect(lambda i: self.set_write_output(self._write_output_choices[bool(i)]))
        self.top_grid_layout.addWidget(_write_output_check_box, 4, 2, 1, 1)
        for r in range(4, 5):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(2, 3):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._trig_level_range = Range(0, 1, 0.01, 0.25, 100)
        self._trig_level_win = RangeWidget(self._trig_level_range, self.set_trig_level, "Trigger (signal magnitude)", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._trig_level_win, 3, 0, 1, 3)
        for r in range(3, 4):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 3):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._thre_low_range = Range(-1, 0, 0.05, -0.2, 100)
        self._thre_low_win = RangeWidget(self._thre_low_range, self.set_thre_low, "Threshold Low", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._thre_low_win, 4, 0, 1, 1)
        for r in range(4, 5):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._thre_high_range = Range(0, 1, 0.05, 0.2, 100)
        self._thre_high_win = RangeWidget(self._thre_high_range, self.set_thre_high, "Threshold High", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._thre_high_win, 4, 1, 1, 1)
        for r in range(4, 5):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._demod_gain_range = Range(1, 5, 0.1, 1, 100)
        self._demod_gain_win = RangeWidget(self._demod_gain_range, self.set_demod_gain, "Demodulator Gain", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._demod_gain_win, 2, 0, 1, 3)
        for r in range(2, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 3):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._samples_per_bit_tool_bar = Qt.QToolBar(self)

        if None:
            self._samples_per_bit_formatter = None
        else:
            self._samples_per_bit_formatter = lambda x: str(x)

        self._samples_per_bit_tool_bar.addWidget(Qt.QLabel("Samples per Bit"))
        self._samples_per_bit_label = Qt.QLabel(str(self._samples_per_bit_formatter(self.samples_per_bit)))
        self._samples_per_bit_tool_bar.addWidget(self._samples_per_bit_label)
        self.top_grid_layout.addWidget(self._samples_per_bit_tool_bar, 0, 2, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(2, 3):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_time_sink_x_1 = qtgui.time_sink_f(
            scope_nb_points, #size
            samp_rate, #samp_rate
            'Demodulated signal', #name
            3, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_1.set_update_time(0.20)
        self.qtgui_time_sink_x_1.set_y_axis(-1.5, 1.5)

        self.qtgui_time_sink_x_1.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_1.enable_tags(True)
        self.qtgui_time_sink_x_1.set_trigger_mode(qtgui.TRIG_MODE_NORM, qtgui.TRIG_SLOPE_POS, trig_level, 0, 0, "")
        self.qtgui_time_sink_x_1.enable_autoscale(False)
        self.qtgui_time_sink_x_1.enable_grid(False)
        self.qtgui_time_sink_x_1.enable_axis_labels(True)
        self.qtgui_time_sink_x_1.enable_control_panel(True)
        self.qtgui_time_sink_x_1.enable_stem_plot(False)


        labels = ['magnitude', 'raw', 'final', 'Signal 4', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['yellow', 'blue', 'red', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(3):
            if len(labels[i]) == 0:
                self.qtgui_time_sink_x_1.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_x_1.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_1.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_1.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_1.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_1.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_1.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_1_win = sip.wrapinstance(self.qtgui_time_sink_x_1.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_time_sink_x_1_win, 5, 0, 1, 3)
        for r in range(5, 6):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 3):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_sink_x_0 = qtgui.sink_c(
            256, #fftsize
            window.WIN_BLACKMAN_hARRIS, #wintype
            frequency, #fc
            samp_rate, #bw
            'Filtered spectrum', #name
            True, #plotfreq
            False, #plotwaterfall
            False, #plottime
            False, #plotconst
            None # parent
        )
        self.qtgui_sink_x_0.set_update_time(1.0/10)
        self._qtgui_sink_x_0_win = sip.wrapinstance(self.qtgui_sink_x_0.qwidget(), Qt.QWidget)

        self.qtgui_sink_x_0.enable_rf_freq(True)

        self.top_grid_layout.addWidget(self._qtgui_sink_x_0_win, 1, 0, 1, 3)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 3):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.osmosdr_source_0 = osmosdr.source(
            args="numchan=" + str(1) + " " + ""
        )
        self.osmosdr_source_0.set_clock_source('external', 0)
        self.osmosdr_source_0.set_sample_rate(samp_rate)
        self.osmosdr_source_0.set_center_freq(frequency, 0)
        self.osmosdr_source_0.set_freq_corr(0, 0)
        self.osmosdr_source_0.set_dc_offset_mode(0, 0)
        self.osmosdr_source_0.set_iq_balance_mode(0, 0)
        self.osmosdr_source_0.set_gain_mode(False, 0)
        self.osmosdr_source_0.set_gain(0, 0)
        self.osmosdr_source_0.set_if_gain(15, 0)
        self.osmosdr_source_0.set_bb_gain(20, 0)
        self.osmosdr_source_0.set_antenna('', 0)
        self.osmosdr_source_0.set_bandwidth(samp_rate, 0)
        # Create the options list
        self._nrf_speed_options = [0, 1, 2]
        # Create the labels list
        self._nrf_speed_labels = ['2Mbps', '1Mbps', '250kbps']
        # Create the combo box
        self._nrf_speed_tool_bar = Qt.QToolBar(self)
        self._nrf_speed_tool_bar.addWidget(Qt.QLabel("nRF Speed" + ": "))
        self._nrf_speed_combo_box = Qt.QComboBox()
        self._nrf_speed_tool_bar.addWidget(self._nrf_speed_combo_box)
        for _label in self._nrf_speed_labels: self._nrf_speed_combo_box.addItem(_label)
        self._nrf_speed_callback = lambda i: Qt.QMetaObject.invokeMethod(self._nrf_speed_combo_box, "setCurrentIndex", Qt.Q_ARG("int", self._nrf_speed_options.index(i)))
        self._nrf_speed_callback(self.nrf_speed)
        self._nrf_speed_combo_box.currentIndexChanged.connect(
            lambda i: self.set_nrf_speed(self._nrf_speed_options[i]))
        # Create the radio buttons
        self.top_grid_layout.addWidget(self._nrf_speed_tool_bar, 0, 0, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._nrf_channel_range = Range(0, 125, 1, 2, 0)
        self._nrf_channel_win = RangeWidget(self._nrf_channel_range, self.set_nrf_channel, "nRF Channel", "counter", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._nrf_channel_win, 0, 1, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.low_pass_filter_0 = filter.fir_filter_ccf(
            1,
            firdes.low_pass(
                1,
                samp_rate,
                lpf_cutoff,
                lpf_tran_width,
                window.WIN_HAMMING,
                6.76))
        self.blocks_threshold_ff_0 = blocks.threshold_ff(thre_low, thre_high, 0)
        self.blocks_selector_0 = blocks.selector(gr.sizeof_char*1,0,write_output)
        self.blocks_selector_0.set_enabled(True)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_char*1)
        self.blocks_float_to_uchar_0 = blocks.float_to_uchar()
        self.blocks_file_sink_0 = blocks.file_sink(gr.sizeof_char*1, '/tmp/fifo_grc', True)
        self.blocks_file_sink_0.set_unbuffered(True)
        self.blocks_complex_to_mag_0 = blocks.complex_to_mag(1)
        self.analog_quadrature_demod_cf_0 = analog.quadrature_demod_cf(demod_gain)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_quadrature_demod_cf_0, 0), (self.blocks_threshold_ff_0, 0))
        self.connect((self.analog_quadrature_demod_cf_0, 0), (self.qtgui_time_sink_x_1, 1))
        self.connect((self.blocks_complex_to_mag_0, 0), (self.qtgui_time_sink_x_1, 0))
        self.connect((self.blocks_float_to_uchar_0, 0), (self.blocks_selector_0, 0))
        self.connect((self.blocks_selector_0, 1), (self.blocks_file_sink_0, 0))
        self.connect((self.blocks_selector_0, 0), (self.blocks_null_sink_0, 0))
        self.connect((self.blocks_threshold_ff_0, 0), (self.blocks_float_to_uchar_0, 0))
        self.connect((self.blocks_threshold_ff_0, 0), (self.qtgui_time_sink_x_1, 2))
        self.connect((self.low_pass_filter_0, 0), (self.analog_quadrature_demod_cf_0, 0))
        self.connect((self.low_pass_filter_0, 0), (self.blocks_complex_to_mag_0, 0))
        self.connect((self.low_pass_filter_0, 0), (self.qtgui_sink_x_0, 0))
        self.connect((self.osmosdr_source_0, 0), (self.low_pass_filter_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "nrf_receiver")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_nrf_speed(self):
        return self.nrf_speed

    def set_nrf_speed(self, nrf_speed):
        self.nrf_speed = nrf_speed
        self.set_lpf_cutoff((1800e3, 900e3, 700e3)[self.nrf_speed])
        self.set_lpf_tran_width((800e3,300e3,250e3)[self.nrf_speed])
        self._nrf_speed_callback(self.nrf_speed)
        self.set_samp_rate((12e6, 6e6, 2e6)[self.nrf_speed])
        self.set_samples_per_bit((6,6,8)[self.nrf_speed])
        self.set_scope_nb_points((1024, 4096, 8192)[self.nrf_speed])

    def get_nrf_channel(self):
        return self.nrf_channel

    def set_nrf_channel(self, nrf_channel):
        self.nrf_channel = nrf_channel
        self.set_frequency(2.4E9+self.nrf_channel*1e6)

    def get_write_output(self):
        return self.write_output

    def set_write_output(self, write_output):
        self.write_output = write_output
        self._write_output_callback(self.write_output)
        self.blocks_selector_0.set_output_index(self.write_output)

    def get_trig_level(self):
        return self.trig_level

    def set_trig_level(self, trig_level):
        self.trig_level = trig_level
        self.qtgui_time_sink_x_1.set_trigger_mode(qtgui.TRIG_MODE_NORM, qtgui.TRIG_SLOPE_POS, self.trig_level, 0, 0, "")

    def get_thre_low(self):
        return self.thre_low

    def set_thre_low(self, thre_low):
        self.thre_low = thre_low
        self.blocks_threshold_ff_0.set_lo(self.thre_low)

    def get_thre_high(self):
        return self.thre_high

    def set_thre_high(self, thre_high):
        self.thre_high = thre_high
        self.blocks_threshold_ff_0.set_hi(self.thre_high)

    def get_scope_nb_points(self):
        return self.scope_nb_points

    def set_scope_nb_points(self, scope_nb_points):
        self.scope_nb_points = scope_nb_points

    def get_samples_per_bit(self):
        return self.samples_per_bit

    def set_samples_per_bit(self, samples_per_bit):
        self.samples_per_bit = samples_per_bit
        Qt.QMetaObject.invokeMethod(self._samples_per_bit_label, "setText", Qt.Q_ARG("QString", str(self._samples_per_bit_formatter(self.samples_per_bit))))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.samp_rate, self.lpf_cutoff, self.lpf_tran_width, window.WIN_HAMMING, 6.76))
        self.osmosdr_source_0.set_sample_rate(self.samp_rate)
        self.osmosdr_source_0.set_bandwidth(self.samp_rate, 0)
        self.qtgui_sink_x_0.set_frequency_range(self.frequency, self.samp_rate)
        self.qtgui_time_sink_x_1.set_samp_rate(self.samp_rate)

    def get_lpf_tran_width(self):
        return self.lpf_tran_width

    def set_lpf_tran_width(self, lpf_tran_width):
        self.lpf_tran_width = lpf_tran_width
        self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.samp_rate, self.lpf_cutoff, self.lpf_tran_width, window.WIN_HAMMING, 6.76))

    def get_lpf_cutoff(self):
        return self.lpf_cutoff

    def set_lpf_cutoff(self, lpf_cutoff):
        self.lpf_cutoff = lpf_cutoff
        self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.samp_rate, self.lpf_cutoff, self.lpf_tran_width, window.WIN_HAMMING, 6.76))

    def get_frequency(self):
        return self.frequency

    def set_frequency(self, frequency):
        self.frequency = frequency
        self.osmosdr_source_0.set_center_freq(self.frequency, 0)
        self.qtgui_sink_x_0.set_frequency_range(self.frequency, self.samp_rate)

    def get_demod_gain(self):
        return self.demod_gain

    def set_demod_gain(self, demod_gain):
        self.demod_gain = demod_gain
        self.analog_quadrature_demod_cf_0.set_gain(self.demod_gain)




def main(top_block_cls=nrf_receiver, options=None):

    if StrictVersion("4.5.0") <= StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()
