import bladeRF

def test_device():
    device = bladeRF.Device()

    device.rx.frequency = 2**28
    assert device.rx.frequency == 2**28
    device.rx.bandwidth = 1500000
    assert device.rx.bandwidth == 1500000
    device.rx.sample_rate = 2**20
    assert device.rx.sample_rate == 2**20

    device.tx.frequency = 1234000000
    assert device.tx.frequency == 1234000000
    device.tx.bandwidth = 1500000
    assert device.tx.bandwidth == 1500000
    device.tx.sample_rate = 2**20
    assert device.tx.sample_rate == 2**20
    
    samples = bladeRF.rx(device.device, bladeRF.FORMAT_SC16_Q12, 1024)
    assert isinstance(samples, bytearray)
    assert len(samples) == 4096
    
