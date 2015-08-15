import bladeRF
from bladeRF import _cffi
from bladeRF._cffi import ffi, cdef, ptop

cdef("""
typedef enum {
    /**
     * Signed, Complex 16-bit Q11. This is the native format of the DAC data.
     *
     * Values in the range [-2048, 2048) are used to represent [-1.0, 1.0).
     * Note that the lower bound here is inclusive, and the upper bound is
     * exclusive. Ensure that provided samples stay within [-2048, 2047].
     *
     * Samples consist of interleaved IQ value pairs, with I being the first
     * value in the pair. Each value in the pair is a right-aligned,
     * little-endian int16_t. The FPGA ensures that these values are
     * sign-extended.
     *
     * When using this format the minimum required buffer size, in bytes, is:
     * <pre>
     *   buffer_size_min = [ 2 * num_samples * sizeof(int16_t) ]
     * </pre>
     *
     * For example, to hold 2048 samples, a buffer must be at least 8192 bytes
     * large.
     */
    BLADERF_FORMAT_SC16_Q11,

    /**
     * This format is the same as the ::BLADERF_FORMAT_SC16_Q11 format, except the
     * first 4 samples (16 bytes) in every block of 1024 samples are replaced
     * with metadata, organized as follows, with all fields being little endian
     * byte order:
     *
     * <pre>
     *  0x00 [uint32_t:  Reserved]
     *  0x04 [uint64_t:  64-bit Timestamp]
     *  0x0c [uint32_t:  BLADERF_META_FLAG_* flags]
     * </pre>
     *
     * When using the bladerf_sync_rx() and bladerf_sync_tx() functions,
     * this detail is transparent to caller. These functions take care of
     * packing/unpacking the metadata into/from the data, via the
     * bladerf_metadata structure.
     *
     * Currently, when using the asynchronous data transfer interface, the user
     * is responsible for manually packing/unpacking this metadata into/from
     * their sample data.
     */
    BLADERF_FORMAT_SC16_Q11_META,
} bladerf_format;

/**
 * For both RX and TX, the stream callback receives:
 * dev:             Device structure
 * stream:          The associated stream
 * metadata:        TBD
 * user_data:       User data provided when initializing stream
 *
 * <br>
 *
 * For TX callbacks:
 *  samples:        Pointer fo buffer of samples that was sent
 *  num_samples:    Number of sent in last transfer and to send in next transfer
 *
 *  Return value:   The user specifies the address of the next buffer to send
 *
 * For RX callbacks:
 *  samples:        Buffer filled with received data
 *  num_samples:    Number of samples received and size of next buffers
 *
 *  Return value:   The user specifies the next buffer to fill with RX data,
 *                  which should be num_samples in size.
 *
 */

typedef void *(*bladerf_stream_cb)(struct bladerf *dev,
                                   struct bladerf_stream *stream,
                                   struct bladerf_metadata *meta,
                                   void *samples,
                                   size_t num_samples,
                                   void *user_data);

// Updated metadata struct, as of 2015-08-15
struct bladerf_metadata {
    uint64_t timestamp;     /**< Timestamp (TODO format TBD) */
    uint32_t flags;         /**< Metadata format flags */
    uint32_t status;         /**< Metadata format status */
    unsigned int actual_count;
    uint8_t reserved[32];
};

""")

def raw_callback(f):
    @ffi.callback('bladerf_stream_cb')
    def handler(dev, stream, meta, samples, num_samples, user_data):
        user_data = ffi.from_handle(user_data)
        v = f(dev, stream, meta, samples, num_samples, user_data)
        if v is None:
            return ffi.NULL
        return v
    return handler


@cdef("""
int  bladerf_init_stream(struct bladerf_stream **stream,
                         struct bladerf *dev,
                         bladerf_stream_cb callback,
                         void ***buffers,
                         size_t num_buffers,
                         bladerf_format format,
                         size_t num_samples,
                         size_t num_transfers,
                         void *user_data);
""")
def init_stream(dev, callback, num_buffers, format, num_samples, num_transfers,
                user_data):
    stream = ffi.new('struct bladerf_stream*[1]')
    buffers = ffi.new('void**[1]')
    err = _cffi.lib.bladerf_init_stream(
        stream, dev, callback, buffers, num_buffers, format, num_samples,
        num_transfers, user_data)
    bladeRF.errors.check_retcode(err)
    return (stream[0], buffers[0])


@cdef('int bladerf_stream(struct bladerf_stream *stream, bladerf_module module);')
def stream(stream, module):
    err = _cffi.lib.bladerf_stream(stream, module)
    bladeRF.errors.check_retcode(err)


@cdef('void bladerf_deinit_stream(struct bladerf_stream *stream);')
def deinit_stream(stream):
    _cffi.lib.bladerf_deinit_stream(stream)


@cdef("""int bladerf_sync_config(struct bladerf *dev,
                                 bladerf_module module,
                                 bladerf_format format,
                                 unsigned int num_buffers,
                                 unsigned int buffer_size,
                                 unsigned int num_transfers,
                                 unsigned int stream_timeout);""")
def sync_config(dev, module, format, num_buffers, buffer_size, num_transfers, stream_timeout):
    err = _cffi.lib.bladerf_sync_config(dev, module, format, num_buffers, buffer_size, num_transfers, stream_timeout)
    bladeRF.errors.check_retcode(err)


@cdef("""int bladerf_sync_tx(struct bladerf *dev,
                            void *samples, unsigned int num_samples,
                            struct bladerf_metadata *metadata,
                            unsigned int timeout_ms);""")
def tx(dev, samples, num_samples, metadata, timeout_ms):
    err = _cffi.lib.bladerf_sync_tx(dev, samples, num_samples, metadata, timeout_ms)
    bladeRF.errors.check_retcode(err)


@cdef("""int bladerf_sync_rx(struct bladerf *dev,
                             void *samples, unsigned int num_samples,
                             struct bladerf_metadata *metadata,
                             unsigned int timeout_ms);""")
def rx(dev, samples, num_samples, metadata, timeout_ms):
    err = _cffi.lib.bladerf_sync_rx(dev, samples, num_samples, metadata, timeout_ms)
    bladeRF.errors.check_retcode(err)

