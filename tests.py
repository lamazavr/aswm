from skimage.io import imread
from skimage.util import random_noise
from skimage import img_as_ubyte

from myhdl import *

from aswm_ref.aswm_fix import weighted_mean, F16, deviation
from hdl.aswm import WMean, WeightsEstimate, Deviation
from aswm_ref.misc import sqrt as sqrt_ref
from hdl.aswm import WMean
from hdl.misc import sqrt

from random import randint

def wmean_testbench():
    path = "img/lena.png"
    img = imread(path, as_grey=True)
    imgn = random_noise(img, mode='s&p', amount=0.75)
    img = img_as_ubyte(imgn)

    clock = Signal(bool(0))

    x = [Signal(intbv(0, min=0, max=2**8)) for _ in range(9)]
    w = [Signal(intbv(0x00010000, min=0, max=2**32)) for _ in range(9)]
    wmean = Signal(intbv(0, min=0, max=2**32))

    cmp_1 = WMean(clock, x[0], x[1], x[2], x[3], x[4], x[5], x[6], x[7], x[8],
                  w[0], w[1], w[2], w[3], w[4], w[5], w[6], w[7], w[8],
                  wmean)

    half_period = delay(10)

    cols, rows = img.shape

    ref_wmean = []
    win = [i for i in range(9)]

    @always(half_period)
    def clock_gen():
        clock.next = not clock

    @instance
    def stimulus():
        yield clock.posedge

        for i in range(1, cols-1):
            for j in range(1, rows-1):

                yield clock.posedge

                x[0].next = int(img[i - 1, j - 1])
                x[1].next = int(img[i, j - 1])
                x[2].next = int(img[i + 1, j - 1])
                x[3].next = int(img[i - 1, j])
                x[4].next = int(img[i, j])
                x[5].next = int(img[i + 1, j])
                x[6].next = int(img[i - 1, j + 1])
                x[7].next = int(img[i, j + 1])
                x[8].next = int(img[i + 1, j + 1])

                # save reference results
                win[0] = int(img[i - 1, j - 1])
                win[1] = int(img[i, j - 1])
                win[2] = int(img[i + 1, j - 1])
                win[3] = int(img[i - 1, j])
                win[4] = int(img[i, j])
                win[5] = int(img[i + 1, j])
                win[6] = int(img[i - 1, j + 1])
                win[7] = int(img[i, j + 1])
                win[8] = int(img[i + 1, j + 1])

                weights = [0x00010000, 0x00010000, 0x00010000,
                           0x00010000, 0x00010000, 0x00010000,
                           0x00010000, 0x00010000, 0x00010000]
                ref_res = weighted_mean(weights, win, 9)
                ref_wmean.append(ref_res)

        # wait for pipeline emptying
        for i in range(0, 8):
            yield clock.posedge

        raise StopSimulation

    @instance
    def monitor():
        # wait for pipeline filling
        for i in range(0, 8):
            yield clock.posedge

        for i in range(1, cols - 1):
            for j in range(1, rows - 1):
                yield clock.posedge

                # get reference
                ref = ref_wmean.pop(0)

                assert ref == wmean, "ref != wnean"

    return clock_gen, stimulus, cmp_1, monitor


def sqrt_testbench():
    clock = Signal(bool(0))
    a = Signal(intbv(0, min=0, max=2**32))
    b = Signal(intbv(0, min=0, max=2**16))

    sqrt_inst = sqrt(clock, a, b)

    half_period = delay(10)

    ref_wmean = []

    @always(half_period)
    def clock_gen():
        clock.next = not clock

    @instance
    def stimulus():
        for i in range(0, 1000):
            yield clock.posedge

            val =  randint(0, 2**32)

            a.next = val

            ref_res = sqrt_ref(val)
            ref_wmean.append(ref_res)

        # wait for pipeline emptying
        for i in range(0, 17):
            yield clock.posedge

        raise StopSimulation

    @instance
    def monitor():
        # wait for pipeline filling
        for i in range(0, 17):
            yield clock.posedge

        for i in range(0, 1000):
            yield clock.posedge

            ref = ref_wmean.pop(0)

            assert ref == b, "ref != hdl sqrt"

    return clock_gen, stimulus, sqrt_inst, monitor

def weights_estimate_testbench():
    clock = Signal(bool(0))

    x = [Signal(modbv(0x00010000)[32:]) for _ in range(9)]
    w = [Signal(modbv(0)[32:]) for _ in range(9)]
    wmean = Signal(modbv(0x8eaaaa)[32:])

    w_inst = WeightsEstimate(clock, wmean,
                             x[0], x[1], x[2], x[3], x[4], x[5], x[6], x[7], x[8],
                             w[0], w[1], w[2], w[3], w[4], w[5], w[6], w[7], w[8])

    half_period = delay(10)

    mean_ref = 0x8eaaaa
    weights = [0, 0, 0, 0, 0, 0, 0, 0, 0]

    ref_weights = []

    @always(half_period)
    def clock_gen():
        clock.next = not clock

    @instance
    def stimulus():
        for i in range(0, 1000):
            yield clock.posedge

            window = [254, 185, 71, 8, 222, 225, 230, 50, 51]
            for i in range(0, 9):
                window[i] = randint(0, 255)

            x[0].next = int(window[0])
            x[1].next = int(window[1])
            x[2].next = int(window[2])
            x[3].next = int(window[3])
            x[4].next = int(window[4])
            x[5].next = int(window[5])
            x[6].next = int(window[6])
            x[7].next = int(window[7])
            x[8].next = int(window[8])

            for l in range(0, 9):
                x_ref = abs((window[l] << 16) - mean_ref) + F16(0.1)
                weights[l] = ((F16(1.0) << 16) / x_ref) << 1

            ref_weights.append(weights[:])

        for i in range(0, 6):
            yield clock.posedge


        raise StopSimulation

    @instance
    def monitor():
        # wait for pipeline filling
        for i in range(0, 5):
            yield clock.posedge


        for i in range(0, 1000):
            yield clock.posedge

            wref = ref_weights.pop(0)

            assert wref == w, "ref != hdl weights estimation"

    return clock_gen, stimulus, w_inst, monitor

def deviation_testbench():
    clock = Signal(bool(0))

    x = [Signal(modbv(0x00010000)[32:]) for _ in range(9)]
    w = [Signal(modbv(0x00010000)[32:]) for _ in range(9)]

    debug =  [Signal(modbv(0x00010000)[32:]) for _ in range(9)]

    wmean = Signal(modbv(0x8106e2)[32:])
    dev = Signal(modbv(0)[32:])

    dev_inst = Deviation(clock,
                         w[0], w[1], w[2], w[3], w[4], w[5], w[6], w[7], w[8],
                         x[0], x[1], x[2], x[3], x[4], x[5], x[6], x[7], x[8],
                         wmean,
                         dev,
                         debug[0],debug[1],debug[2],debug[3],debug[4],debug[5],debug[6],debug[7],debug[8])

    half_period = delay(10)

    mean_ref = 0x8106e2
    dev_ref = 0

    @always(half_period)
    def clock_gen():
        clock.next = not clock

    @instance
    def stimulus():
        for i in range(0, 50):
            yield clock.posedge

            window = [255, 0, 128, 129, 130, 127, 255, 255, 0]
            weights = [1040, 1014, 111298, 737776, 128208, 60188, 1040, 1040, 1014]
            # dev 2294
            # acc 1042618
            # wacc 83760562

            #for i in range(0, 9):
            #    window[i] = randint(0, 255)

            x[0].next = int(window[0])
            x[1].next = int(window[1])
            x[2].next = int(window[2])
            x[3].next = int(window[3])
            x[4].next = int(window[4])
            x[5].next = int(window[5])
            x[6].next = int(window[6])
            x[7].next = int(window[7])
            x[8].next = int(window[8])

            w[0].next = int(weights[0])
            w[1].next = int(weights[1])
            w[2].next = int(weights[2])
            w[3].next = int(weights[3])
            w[4].next = int(weights[4])
            w[5].next = int(weights[5])
            w[6].next = int(weights[6])
            w[7].next = int(weights[7])
            w[8].next = int(weights[8])


            dev_ref = deviation(weights, window, mean_ref, 9)

        for i in range(0, 6):
            yield clock.posedge


        raise StopSimulation

    @instance
    def monitor():
        # wait for pipeline filling
        for i in range(0,25):
            yield clock.posedge

            print(i, dev)

        for i in range(0,50):
            yield clock.posedge

            print(i, dev)


    return clock_gen, stimulus, dev_inst, monitor


if __name__ == "__main__":
    # print("testing sqrt ...")
    # sqrt_tb = sqrt_testbench()
    # Simulation(sqrt_tb).run()
    #
    # print("testing wmean ...")
    # wmean_tb = wmean_testbench()
    # Simulation(wmean_tb).run()
    #
    # print("testing weights estimate ...")
    # west_tb = weights_estimate_testbench()
    # Simulation(west_tb).run()

    print("testing deviation ...")
    dev_tb = deviation_testbench()
    Simulation(dev_tb).run()
