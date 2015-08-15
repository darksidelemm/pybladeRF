import bladeRF
from bladeRF import _cffi
from bladeRF._cffi import ffi, cdef, ptop

# Enumerations directly from libbladeRF.h, as of 2015-08-15
cdef("""
/**
 * Sampling connection
 */
typedef enum {
    BLADERF_SAMPLING_UNKNOWN,  /**< Unable to determine connection type */
    BLADERF_SAMPLING_INTERNAL, /**< Sample from RX/TX connector */
    BLADERF_SAMPLING_EXTERNAL  /**< Sample from J60 or J61 */
} bladerf_sampling;

/**
 * LNA gain options
 */
typedef enum {
    BLADERF_LNA_GAIN_UNKNOWN,    /**< Invalid LNA gain */
    BLADERF_LNA_GAIN_BYPASS,     /**< LNA bypassed - 0dB gain */
    BLADERF_LNA_GAIN_MID,        /**< LNA Mid Gain (MAX-6dB) */
    BLADERF_LNA_GAIN_MAX         /**< LNA Max Gain */
} bladerf_lna_gain;

/**
 * LPF mode
 */
typedef enum {
    BLADERF_LPF_NORMAL,     /**< LPF connected and enabled */
    BLADERF_LPF_BYPASSED,   /**< LPF bypassed */
    BLADERF_LPF_DISABLED    /**< LPF disabled */
} bladerf_lpf_mode;

/**
 * Module selection for those which have both RX and TX constituents
 */
typedef enum
{
    BLADERF_MODULE_RX,  /**< Receive Module */
    BLADERF_MODULE_TX   /**< Transmit Module */
} bladerf_module;

/**
 * Expansion boards
 */
typedef enum {
    BLADERF_XB_NONE = 0,
    BLADERF_XB_100,
    BLADERF_XB_200
} bladerf_xb ;

/**
 * XB 200 filterbanks
 */
typedef enum {
    BLADERF_XB200_50M = 0,
    BLADERF_XB200_144M,
    BLADERF_XB200_222M,
    BLADERF_XB200_CUSTOM
} bladerf_xb200_filter;

/**
 * XB 200 signal paths
 */
typedef enum {
    BLADERF_XB200_BYPASS = 0,
    BLADERF_XB200_MIX
} bladerf_xb200_path;

/**
 * DC Calibration Modules
 */
typedef enum
{
    BLADERF_DC_CAL_LPF_TUNING,
    BLADERF_DC_CAL_TX_LPF,
    BLADERF_DC_CAL_RX_LPF,
    BLADERF_DC_CAL_RXVGA2
} bladerf_cal_module;

/**
 * Correction parameter selection
 *
 * These values specify the correction parameter to modify or query when
 * calling bladerf_set_correction() or bladerf_get_correction(). Note that the
 * meaning of the `value` parameter to these functions depends upon the
 * correction parameter.
 *
 */
typedef enum
{
    /**
     * Adjusts the in-phase DC offset via controls provided by the LMS6002D
     * front end. Valid values are [-2048, 2048], which are scaled to the
     * available control bits in the LMS device.
     */
    BLADERF_CORR_LMS_DCOFF_I,

    /**
     * Adjusts the quadrature DC offset via controls provided the LMS6002D
     * front end. Valid values are [-2048, 2048], which are scaled to the
     * available control bits.
     */
    BLADERF_CORR_LMS_DCOFF_Q,

    /**
     * Adjusts FPGA-based phase correction of [-10, 10] degrees, via a provided
     * count value of [-4096, 4096].
     */
    BLADERF_CORR_FPGA_PHASE,

    /**
     * Adjusts FPGA-based gain correction of [0.0, 2.0], via provided
     * values in the range of [-4096, 4096], where a value of 0 corresponds to
     * a gain of 1.0.
     */
    BLADERF_CORR_FPGA_GAIN
} bladerf_correction;
""")

@cdef('int bladerf_enable_module(struct bladerf *dev, '
      'bladerf_module m, bool enable);')
def enable_module(dev, module, enable):
    err = _cffi.lib.bladerf_enable_module(dev, module, enable)
    bladeRF.errors.check_retcode(err)


@cdef('int bladerf_set_sample_rate(struct bladerf *dev, '
      'bladerf_module module, unsigned int rate, unsigned int *actual);')
def set_sample_rate(dev, module, rate):
    actual = ffi.new('unsigned int*')
    err = _cffi.lib.bladerf_set_sample_rate(dev, module, int(rate), actual)
    bladeRF.errors.check_retcode(err)
    return int(actual[0])


@cdef('int bladerf_set_sampling(struct bladerf *dev, bladerf_sampling sampling);')
def set_sampling(dev, sampling):
    err = _cffi.lib.bladerf_set_sampling(dev, sampling)
    bladeRF.errors.check_retcode(err)


@cdef('int bladerf_get_sampling(struct bladerf *dev, bladerf_sampling *sampling);')
def get_sampling(dev):
    sampling = ffi.new('bladerf_sampling*')
    err = _cffi.lib.bladerf_get_sampling(dev, sampling)
    bladeRF.errors.check_retcode(err)
    return int(sampling[0])


@cdef('int bladerf_get_sample_rate(struct bladerf *dev, bladerf_module module, unsigned int *rate);')
def get_sample_rate(dev, module):
    rate = ffi.new('unsigned int *')
    err = _cffi.lib.bladerf_get_sample_rate(dev, module, rate)
    bladeRF.errors.check_retcode(err)
    return int(rate[0])


@cdef('int bladerf_get_rational_sample_rate(struct bladerf *dev,'
      'bladerf_module module, struct bladerf_rational_rate *rate);')
def get_rational_sample_rate(dev, module):
    pass


@cdef('int bladerf_set_txvga2(struct bladerf *dev, int gain);')
def set_txvga2(dev, gain):
    err = _cffi.lib.bladerf_set_txvga2(dev, gain)
    bladeRF.errors.check_retcode(err)


@cdef('int bladerf_get_txvga2(struct bladerf *dev, int *gain);')
def get_txvga2(dev):
    gain = ffi.new('int *')
    err = _cffi.lib.bladerf_get_txvga2(dev, gain)
    bladeRF.errors.check_retcode(err)
    return int(gain[0])


@cdef('int bladerf_set_txvga1(struct bladerf *dev, int gain);')
def set_txvga1(dev, gain):
    err = _cffi.lib.bladerf_set_txvga1(dev, gain)
    bladeRF.errors.check_retcode(err)
    

@cdef('int bladerf_get_txvga1(struct bladerf *dev, int *gain);')
def get_txvga1(dev):
    gain = ffi.new('int *')
    err = _cffi.lib.bladerf_get_txvga1(dev, gain)
    bladeRF.errors.check_retcode(err)
    return int(gain[0])


@cdef('int bladerf_set_lna_gain(struct bladerf *dev, bladerf_lna_gain gain);')
def set_lna_gain(dev, gain):
    err = _cffi.lib.bladerf_set_lna_gain(dev, gain)
    bladeRF.errors.check_retcode(err)


@cdef('int bladerf_get_lna_gain(struct bladerf *dev, bladerf_lna_gain *gain);')
def get_lna_gain(dev):
    gain = ffi.new('bladerf_lna_gain *')
    err = _cffi.lib.bladerf_get_lna_gain(dev, gain)
    bladeRF.errors.check_retcode(err)
    return int(gain[0])


@cdef('int bladerf_set_rxvga1(struct bladerf *dev, int gain);')
def set_rxvga1(dev, gain):
    err = _cffi.lib.bladerf_set_rxvga1(dev, gain)
    bladeRF.errors.check_retcode(err)


@cdef('int bladerf_get_rxvga1(struct bladerf *dev, int *gain);')
def get_rxvga1(dev):
    gain = ffi.new('int *')
    err = _cffi.lib.bladerf_get_rxvga1(dev, gain)
    bladeRF.errors.check_retcode(err)
    return int(gain[0])


@cdef('int bladerf_set_rxvga2(struct bladerf *dev, int gain);')
def set_rxvga2(dev, gain):
    err = _cffi.lib.bladerf_set_rxvga2(dev, gain)
    bladeRF.errors.check_retcode(err)


@cdef('int bladerf_get_rxvga2(struct bladerf *dev, int *gain);')
def get_rxvga2(dev):
    gain = ffi.new('int *')
    err = _cffi.lib.bladerf_get_rxvga2(dev, gain)
    bladeRF.errors.check_retcode(err)
    return int(gain[0])


@cdef('int bladerf_set_bandwidth(struct bladerf *dev, bladerf_module module, '
      'unsigned int bandwidth, unsigned int *actual);')
def set_bandwidth(dev, module, bandwidth):
    actual = ffi.new('unsigned int *')
    err = _cffi.lib.bladerf_set_bandwidth(dev, module, bandwidth, actual)
    bladeRF.errors.check_retcode(err)
    return int(actual[0])


@cdef('int bladerf_get_bandwidth(struct bladerf *dev, bladerf_module module, '
      'unsigned int *bandwidth);')
def get_bandwidth(dev, module):
    bandwidth = ffi.new('unsigned int *')
    err = _cffi.lib.bladerf_get_bandwidth(dev, module, bandwidth)
    bladeRF.errors.check_retcode(err)
    return int(bandwidth[0])


@cdef('int bladerf_set_lpf_mode(struct bladerf *dev, bladerf_module module, '
      'bladerf_lpf_mode mode);')
def set_lpf_mode(dev, module, mode):
    err = _cffi.lib.bladerf_set_lpf_mode(dev, module, mode)
    bladeRF.errors.check_retcode(err)


@cdef('int bladerf_get_lpf_mode(struct bladerf *dev, bladerf_module module,'
      'bladerf_lpf_mode *mode);')
def get_lpf_mode(dev, module):
    mode = ffi.new('bladerf_lpf_mode *')
    err = _cffi.lib.bladerf_get_lpf_mode(dev, module, mode)
    bladeRF.errors.check_retcode(err)
    return int(mode[0])


@cdef('int bladerf_select_band(struct bladerf *dev, bladerf_module module,'
      'unsigned int frequency);')
def select_band(dev, module, frequency):
    err = _cffi.lib.bladerf_select_band(dev, module, frequency)
    bladeRF.errors.check_retcode(err)


@cdef('int bladerf_set_frequency(struct bladerf *dev, '
      'bladerf_module module, unsigned int frequency);')
def set_frequency(dev, module, frequency):
    err = _cffi.lib.bladerf_set_frequency(dev, module, int(frequency))
    bladeRF.errors.check_retcode(err)


@cdef('int bladerf_get_frequency(struct bladerf *dev,'
      'bladerf_module module, unsigned int *frequency);')
def get_frequency(dev, module):
    frequency = ffi.new('unsigned int *')
    err = _cffi.lib.bladerf_get_frequency(dev, module, frequency)
    bladeRF.errors.check_retcode(err)
    return int(frequency[0])


@cdef('int bladerf_expansion_attach(struct bladerf *dev, bladerf_xb xb);')
def expansion_attach(dev, xb):
    err = _cffi.lib.bladerf_expansion_attach(dev,xb)
    bladeRF.errors.check_retcode(err)

@cdef('int bladerf_expansion_get_attached(struct bladerf *dev, bladerf_xb *xb);')
def expansion_get_attached(dev):
    xb = ffi.new('bladerf_xb *')
    err = _cffi.lib.bladerf_expansion_get_attached(dev, xb)
    bladeRF.errors.check_retcode(err)
    return int(xb[0])

@cdef('int bladerf_xb200_set_filterbank(struct bladerf *dev, bladerf_module mod, bladerf_xb200_filter filter);')
def xb200_set_filterbank(dev, module, filter):
    err = _cffi.lib.bladerf_xb200_set_filterbank(dev,module,filter)
    bladeRF.errors.check_retcode(err)

@cdef('int bladerf_xb200_get_filterbank(struct bladerf *dev, bladerf_module mod, bladerf_xb200_filter *filter);')
def xb200_get_filterbank(dev,module):
    filter = ffi.new('bladerf_xb200_filter *')
    err = _cffi.lib.bladerf_xb200_get_filterbank(dev,module,filter)
    bladeRF.errors.check_retcode(err)
    return int(filter[0])

@cdef('int bladerf_xb200_set_path(struct bladerf *dev, bladerf_module module, bladerf_xb200_path path);')
def xb200_set_path(dev,module,path):
    err = _cffi.lib.bladerf_xb200_set_path(dev,module,path)
    bladeRF.errors.check_retcode(err)

@cdef('int bladerf_xb200_get_path(struct bladerf *dev, bladerf_module module, bladerf_xb200_path *path);')
def xb200_get_path(dev,module):
    path = ffi.new('bladerf_xb200_path *')
    err = _cffi.lib.bladerf_xb200_get_path(dev,module,path)
    bladeRF.errors.check_retcode(err)
    return int(path[0])
