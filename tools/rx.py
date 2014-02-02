"""\
bladeRF Receiver

Usage:
  rx.py <frequency> [options]
  rx.py (-h | --help)
  rx.py --version

Options:
  -h --help                Show this screen.
  -v --version             Show version.
  -d --device=<d>          Device identifier [default: ]
  -f --file=<f>            File to write samples to [default: -].
  -b --bandwidth=<bw>      Bandwidth in Hertz [default: 7000000].
  -s --sample-rate=<sr>    Sample rate in samples per second [default: 10000000].
  -n --num-buffers=<nb>    Number of transfer buffers [default: 32].
  -t --num-transfers=<nt>  Number of transfers [default: 1].
  -l --num-samples=<ns>    Numper of samples per transfer buffer [default: 4096].
  -g --lna-gain=<lg>       Set LNA gain [default: LNA_GAIN_MAX]
  -o --vga1-gain=<lg>      Set vga1 [default: 21]
  -w --vga2-gain=<sq>      Set vga2 squelch [default: 17]
  -q --squelch=<sq>        Set squelch [default: 0]
"""
import sys
import bladeRF
from docopt import docopt


if __name__ == '__main__':
    args = docopt(__doc__, version='bladeRF Receiver 1.0')
    outfile = sys.stdout if args['--file'] == '-' else open(args['--file'], 'wb')

    device = bladeRF.Device(args['--device'])

    device.rx.enabled = True
    device.rx.frequency = int(args['<frequency>'])
    device.rx.bandwidth = int(args['--bandwidth'])
    device.rx.sample_rate = int(args['--sample-rate'])
    device.lna_gain = getattr(bladeRF, args['--lna-gain'])
    device.rx.vga1 = int(args['--vga1-gain'])
    device.rx.vga2 = int(args['--vga2-gain'])
    squelch = float(args['--squelch'])

    def rx(device, stream, meta_data, samples, num_samples, user_data):
        samples = bladeRF.samples_to_narray(samples, num_samples)
        if bladeRF.squelched(samples, squelch):
            return stream.current()
        outfile.write(stream.current_as_buffer())
        return stream.next()

    stream = device.rx.stream(
        rx,
        int(args['--num-buffers']),
        bladeRF.FORMAT_SC16_Q12,
        int(args['--num-samples']),
        int(args['--num-transfers']),
        )

    stream.run()



