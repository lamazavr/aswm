from myhdl import *
from hdl.misc import *

def Multiplier(clk, x, w, wx):

    @always(clk.posedge)
    def MultiplierLogic():
        wx.next = (w * x << 16) >> 16

    return MultiplierLogic

def Adder(clk, a, b, outp):

    @always(clk.posedge)
    def AdderLogic():
        outp.next = a + b

    return AdderLogic

def FracDiv(clk, num, den, q):

    @always(clk.posedge)
    def FracDivLogic():
        q.next = ((num << 15) // den) << 1

    return FracDivLogic

def FracDiv2(clk, num, den, q):

    @always(clk.posedge)
    def FracDiv2Logic():
        q.next = ((num << 16) // den) << 1

    return FracDiv2Logic


def WMean(clk,
          x0, x1, x2, x3, x4, x5, x6, x7, x8,
          w0, w1, w2, w3, w4, w5, w6, w7, w8,
          wmean):

    x = [x0, x1, x2, x3, x4, x5, x6, x7, x8]
    w = [w0, w1, w2, w3, w4, w5, w6, w7, w8]
    add_l_0 = [Signal(intbv(0, min=w0.min, max=w0.max)) for i in range(9)]
    add_l_1 = [Signal(intbv(0, min=w0.min, max=w0.max)) for i in range(5)]
    add_l_2 = [Signal(intbv(0, min=w0.min, max=w0.max)) for i in range(3)]
    add_l_3 = [Signal(intbv(0, min=w0.min, max=w0.max)) for i in range(2)]
    y = [Signal(intbv(0, min=x0.min, max=x0.max)) for i in range(9)]

    # multiplying each input
    mull_inst = []
    for i in range(9):
        mull_inst.append(Multiplier(clk, x[i], w[i], add_l_0[i]))

    # Calculation of weighted sum in 4clks
    wacc = Signal(intbv(0, min=w0.min, max=w0.max))

    adder_inst_0 = Adder(clk, add_l_0[0], add_l_0[1], add_l_1[0])
    adder_inst_1 = Adder(clk, add_l_0[2], add_l_0[3], add_l_1[1])
    adder_inst_2 = Adder(clk, add_l_0[4], add_l_0[5], add_l_1[2])
    adder_inst_3 = Adder(clk, add_l_0[6], add_l_0[7], add_l_1[3])

    adder_inst_4 = Adder(clk, add_l_1[0], add_l_1[1], add_l_2[0])
    adder_inst_5 = Adder(clk, add_l_1[2], add_l_1[3], add_l_2[1])

    adder_inst_6 = Adder(clk, add_l_2[0], add_l_2[1], add_l_3[0])

    adder_inst_7 = Adder(clk, add_l_3[0], add_l_3[1], wacc)

    # Registers to pipeline calculations
    reg_inst_0 = Register(clk, add_l_0[8], add_l_1[4])
    reg_inst_1 = Register(clk, add_l_1[4], add_l_2[2])
    reg_inst_2 = Register(clk, add_l_2[2], add_l_3[1])

    # Calculation of weights sum in 4clks
    # Init signals with 1 to prevent div by 0
    acc = Signal(intbv(1, min=w0.min, max=w0.max))
    acc_0 = Signal(intbv(1, min=w0.min, max=w0.max))

    wsum_l_0 = [Signal(intbv(1, min=w0.min, max=w0.max)) for i in range(5)]
    wsum_l_1 = [Signal(intbv(1, min=w0.min, max=w0.max)) for i in range(3)]
    wsum_l_2 = [Signal(intbv(1, min=w0.min, max=w0.max)) for i in range(2)]

    adder_inst_8 = Adder(clk, w[0], w[1], wsum_l_0[0])
    adder_inst_9 = Adder(clk, w[2], w[3], wsum_l_0[1])
    adder_inst_10 = Adder(clk, w[4], w[5], wsum_l_0[2])
    adder_inst_11 = Adder(clk, w[6], w[7], wsum_l_0[3])

    adder_inst_12 = Adder(clk, wsum_l_0[0], wsum_l_0[1], wsum_l_1[0])
    adder_inst_13 = Adder(clk, wsum_l_0[2], wsum_l_0[3], wsum_l_1[1])

    adder_inst_14 = Adder(clk, wsum_l_1[0], wsum_l_1[1], wsum_l_2[0])

    adder_inst_15 = Adder(clk, wsum_l_2[0], wsum_l_2[1], acc_0)

    # Registers to pipeline calculations
    reg_inst_3 = Register(clk, w[8], wsum_l_0[4])
    reg_inst_4 = Register(clk, wsum_l_0[4], wsum_l_1[2])
    reg_inst_5 = Register(clk, wsum_l_1[2], wsum_l_2[1])

    reg_inst_6 = Register(clk, acc_0, acc)

    # Calculate weighted mean
    div_inst = FracDiv(clk, wacc, acc, wmean)

    return instances()

def WeightsEstimate(clk,
                    wmean,
                    x0, x1, x2, x3, x4, x5, x6, x7, x8,
                    w0, w1, w2, w3, w4, w5, w6, w7, w8):

    x = [x0, x1, x2, x3, x4, x5, x6, x7, x8]
    w = [w0, w1, w2, w3, w4, w5, w6, w7, w8]

    sub_0 = [Signal(modbv(0, min=0, max=2**32)) for i in range(9)]
    sub_1 = [Signal(modbv(0, min=0, max=2**32)) for i in range(9)]
    sub_2 = [Signal(modbv(0, min=0, max=2**32)) for i in range(9)]
    signs_0 = [Signal(bool(0)) for i in range(9)]

    add_0 = [Signal(modbv(0x2000, min=0, max=2**32)) for i in range(9)]

    sub_inst = []
    for i in range(9):
       sub_inst.append(Sub2(clk, x[i], wmean, sub_0[i], sub_1[i], signs_0[i]))

    mux_inst = []
    for i in range(9):
        mux_inst.append(Mux2(clk, signs_0[i], sub_0[i], sub_1[i], sub_2[i]))

    add_const = Signal(intbv(0x1999, min=0, max=2**32))

    add_inst = []
    for i in range(9):
        add_inst.append(Adder(clk, sub_2[i], add_const, add_0[i]))

    div_num = Signal(intbv(0x10000, min=0, max=2**32))

    div_inst = []
    for i in range(9):
        div_inst.append(FracDiv2(clk, div_num, add_0[i], w[i]))


    return instances()


"""
def deviation(weights, window, mean, size):
    acc = 0
    wacc = 0

    for i in range(0, size):
        diff = (window[i] << 16) - mean
        ddiff = frac_mul(diff, diff)

        wacc = wacc + frac_mul(weights[i], ddiff)
        acc = acc + weights[i]

    return frac_sqrt(frac_div(wacc, acc))
"""



def Deviation(clk,
              w0, w1, w2, w3, w4, w5, w6, w7, w8,
              win0, win1, win2, win3, win4, win5, win6, win7, win8,
              wmean,
              deviation):

    win = [win0, win1, win2, win3, win4, win5, win6, win7, win8]
    w = [w0, w1, w2, w3, w4, w5, w6, w7, w8]

    diff_l_0 = [Signal(modbv(0x00020000, min=-2**32, max=2**32)) for i in range(9)]
    diff_l_1 = [Signal(modbv(1, min=-2**64, max=2**64)) for i in range(9)]
    wdiff_l_0 = [Signal(modbv(1, min=-2**64, max=2**64)) for i in range(9)]
    # print(win)
    diff_inst_0 = []
    for i in range(9):
        diff_inst_0.append(Diff(clk, wmean, win[i], diff_l_0[i]))

    diff_inst_1 = []
    for i in range(9):
        diff_inst_1.append(Pow2(clk, diff_l_0[i], diff_l_1[i]))


    # w pipeline for 2clks
    w_delay_l_0 = [Signal(modbv(0x00010000, min=w0.min, max=w0.max)) for i in range(9)]
    w_delay_l_1 = [Signal(modbv(0x00010000, min=w0.min, max=w0.max)) for i in range(9)]

    w_delay_regs_inst_0 = []
    for i in range(9):
        w_delay_regs_inst_0.append(Register(clk, w[i], w_delay_l_0[i]))

    w_delay_regs_inst_1 = []
    for i in range(9):
        w_delay_regs_inst_1.append(Register(clk, w_delay_l_0[i], w_delay_l_1[i]))


    wdiff_inst_0 = []
    for i in range(9):
        wdiff_inst_0.append(Mul2(clk, diff_l_1[i], w_delay_l_1[i], wdiff_l_0[i]))



    wacc = Signal(modbv(1, min=-2**64, max=2**64))

    add_wacc_l_0 = [Signal(modbv(1, min=-2**64, max=2**64)) for i in range(5)]
    add_wacc_l_1 = [Signal(modbv(1, min=-2**64, max=2**64)) for i in range(3)]
    add_wacc_l_2 = [Signal(modbv(1, min=-2**64, max=2**64)) for i in range(2)]

    adder_inst_0 = Adder(clk, wdiff_l_0[0], wdiff_l_0[1], add_wacc_l_0[0])
    adder_inst_1 = Adder(clk, wdiff_l_0[2], wdiff_l_0[3], add_wacc_l_0[1])
    adder_inst_2 = Adder(clk, wdiff_l_0[4], wdiff_l_0[5], add_wacc_l_0[2])
    adder_inst_3 = Adder(clk, wdiff_l_0[6], wdiff_l_0[7], add_wacc_l_0[3])

    adder_inst_4 = Adder(clk, add_wacc_l_0[0], add_wacc_l_0[1], add_wacc_l_1[0])
    adder_inst_5 = Adder(clk, add_wacc_l_0[2], add_wacc_l_0[3], add_wacc_l_1[1])

    adder_inst_6 = Adder(clk, add_wacc_l_1[0], add_wacc_l_1[1], add_wacc_l_2[0])

    adder_inst_7 = Adder(clk, add_wacc_l_2[0], add_wacc_l_2[1], wacc)

    # Registers to pipeline wacc calculation
    reg_inst_0 = Register(clk, wdiff_l_0[8], add_wacc_l_0[4])
    reg_inst_1 = Register(clk, add_wacc_l_0[4], add_wacc_l_1[2])
    reg_inst_2 = Register(clk, add_wacc_l_1[2], add_wacc_l_2[1])


    acc = Signal(intbv(1, min=w0.min, max=w0.max))

    add_acc_l_0 = [Signal(modbv(1, min=w0.min, max=w0.max)) for i in range(5)]
    add_acc_l_1 = [Signal(modbv(1, min=w0.min, max=w0.max)) for i in range(3)]
    add_acc_l_2 = [Signal(modbv(1, min=w0.min, max=w0.max)) for i in range(2)]

    add_acc_l_3 = Signal(modbv(1, min=w0.min, max=w0.max))
    add_acc_l_4 = Signal(modbv(1, min=w0.min, max=w0.max))
    add_acc_l_5 = Signal(modbv(1, min=w0.min, max=w0.max))

    adder_acc_inst_0 = Adder(clk, w[0], w[1], add_acc_l_0[0])
    adder_acc_inst_1 = Adder(clk, w[2], w[3], add_acc_l_0[1])
    adder_acc_inst_2 = Adder(clk, w[4], w[5], add_acc_l_0[2])
    adder_acc_inst_3 = Adder(clk, w[6], w[7], add_acc_l_0[3])

    adder_acc_inst_4 = Adder(clk, add_acc_l_0[0], add_acc_l_0[1], add_acc_l_1[0])
    adder_acc_inst_5 = Adder(clk, add_acc_l_0[2], add_acc_l_0[3], add_acc_l_1[1])

    adder_acc_inst_6 = Adder(clk, add_acc_l_1[0], add_acc_l_1[1], add_acc_l_2[0])

    adder_acc_inst_7 = Adder(clk, add_acc_l_2[0], add_acc_l_2[1], add_acc_l_3)


    # Registers to pipeline acc calculation
    reg_acc_inst_0 = Register(clk, w[8], add_acc_l_0[4])
    reg_acc_inst_1 = Register(clk, add_acc_l_0[4], add_acc_l_1[2])
    reg_acc_inst_2 = Register(clk, add_acc_l_1[2], add_acc_l_2[1])

    reg_acc_inst_3 = Register(clk, add_acc_l_3, add_acc_l_4)
    reg_acc_inst_4 = Register(clk, add_acc_l_4, add_acc_l_5)
    reg_acc_inst_5 = Register(clk, add_acc_l_5, acc)


    div_response = Signal(modbv(1, min=w0.min, max=w0.max))

    div_inst = FracDiv(clk, wacc, acc, div_response)
    sqrt_inst = sqrt(clk, div_response, deviation)

    return instances()


def wmean_diff(clk, mean, new_mean, ready):

    acc = Signal(modbv(1, min=mean.min, max=mean.max))
    acc_abs = Signal(modbv(1, min=mean.min, max=mean.max))
    cmp_acc = Signal(modbv(1, min=mean.min, max=mean.max))

    @always(clk.posedge)
    def SubLogic():
        acc.next = mean - new_mean

    @always(clk.posedge)
    def AbsLogic():
        if acc & 0x80008000:
            acc_abs.next = -acc
        else:
            acc_abs.next = acc

    @always(clk.posedge)
    def ReadyLogic():
        if acc_abs < 6553:
            ready.next = 1
        else:
            ready.next = 0

    return instances()

def loop_block(clk,
               mean,
               bypass_in,
               w0, w1, w2, w3, w4, w5, w6, w7, w8,
               win0, win1, win2, win3, win4, win5, win6, win7, win8,
               wout0, wout1, wout2, wout3, wout4, wout5, wout6, wout7, wout8,
               new_mean,
               bypass):

    wmean = Signal(intbv(1, min=mean.min, max=mean.max))

    # win = [win0, win1, win2, win3, win4, win5, win6, win7, win8]
    # weights_out = [wout0, wout1, wout2, wout3, wout4, wout5, wout6, wout7, wout8]
    # weights_in = [w0, w1, w2, w3, w4, w5, w6, w7, w8]



    win = [Signal(modbv(1, min=win0.min, max=win0.max)) for _ in range(9)]
    weights_out = [Signal(modbv(1, min=wout0.min, max=wout0.max)) for _ in range(9)]
    weights_in = [Signal(modbv(1, min=w0.min, max=w0.max)) for _ in range(9)]

    win[0] = win0
    win[1] = win1
    win[2] = win2
    win[3] = win3
    win[4] = win4
    win[5] = win5
    win[6] = win6
    win[7] = win7
    win[8] = win8

    weights_in[0] = w0
    weights_in[1] = w1
    weights_in[2] = w2
    weights_in[3] = w3
    weights_in[4] = w4
    weights_in[5] = w5
    weights_in[6] = w6
    weights_in[7] = w7
    weights_in[8] = w8

    bypass_pipe_0 = [Signal(bool(0)) for _ in range(14)]
    bypass_0 = Signal(bool(0))

    bypass_regs_inst = []
    bypass_regs_inst.append(Register(clk, bypass_in, bypass_pipe_0[13]))
    for i in range(0, 13):
        bypass_regs_inst.append(Register(clk, bypass_pipe_0[i+1], bypass_pipe_0[i]))

    # pipeline wout for 8clks here
    wout_pipe_0 = [Signal(modbv(1, min=w0.min, max=w0.max)) for _ in range(9)]
    wout_pipe_1 = [Signal(modbv(1, min=w0.min, max=w0.max)) for _ in range(9)]
    wout_pipe_2 = [Signal(modbv(1, min=w0.min, max=w0.max)) for _ in range(9)]
    wout_pipe_3 = [Signal(modbv(1, min=w0.min, max=w0.max)) for _ in range(9)]
    wout_pipe_4 = [Signal(modbv(1, min=w0.min, max=w0.max)) for _ in range(9)]
    wout_pipe_5 = [Signal(modbv(1, min=w0.min, max=w0.max)) for _ in range(9)]
    wout_pipe_6 = [Signal(modbv(1, min=w0.min, max=w0.max)) for _ in range(9)]
    wout_pipe_7 = [Signal(modbv(1, min=w0.min, max=w0.max)) for _ in range(9)]
    wout_pipe_8 = [Signal(modbv(1, min=w0.min, max=w0.max)) for _ in range(9)]
    wout_pipe_9 = [Signal(modbv(1, min=w0.min, max=w0.max)) for _ in range(9)]

    win_pipe_0 = [Signal(intbv(0, min=0, max=2**8)) for _ in range(9)]
    win_pipe_1 = [Signal(intbv(0, min=0, max=2**8)) for _ in range(9)]
    win_pipe_2 = [Signal(intbv(0, min=0, max=2**8)) for _ in range(9)]
    win_pipe_3 = [Signal(intbv(0, min=0, max=2**8)) for _ in range(9)]

    weigths_in_pipe_0 = [Signal(intbv(0, min=w0.min, max=w0.max)) for _ in range(9)]
    weigths_in_pipe_1 = [Signal(intbv(0, min=w0.min, max=w0.max)) for _ in range(9)]
    weigths_in_pipe_2 = [Signal(intbv(0, min=w0.min, max=w0.max)) for _ in range(9)]
    weigths_in_pipe_3 = [Signal(intbv(0, min=w0.min, max=w0.max)) for _ in range(9)]
    weigths_in_pipe_4 = [Signal(intbv(0, min=w0.min, max=w0.max)) for _ in range(9)]
    weigths_in_pipe_5 = [Signal(intbv(0, min=w0.min, max=w0.max)) for _ in range(9)]
    weigths_in_pipe_6 = [Signal(intbv(0, min=w0.min, max=w0.max)) for _ in range(9)]
    weigths_in_pipe_7 = [Signal(intbv(0, min=w0.min, max=w0.max)) for _ in range(9)]
    weigths_in_pipe_8 = [Signal(intbv(0, min=w0.min, max=w0.max)) for _ in range(9)]
    weigths_in_pipe_9 = [Signal(intbv(0, min=w0.min, max=w0.max)) for _ in range(9)]
    weigths_in_pipe_10 = [Signal(intbv(0, min=w0.min, max=w0.max)) for _ in range(9)]
    weigths_in_pipe_11 = [Signal(intbv(0, min=w0.min, max=w0.max)) for _ in range(9)]
    weigths_in_pipe_12 = [Signal(intbv(0, min=w0.min, max=w0.max)) for _ in range(9)]

    win_pipe_inst_0 = []
    win_pipe_inst_1 = []
    win_pipe_inst_2 = []
    win_pipe_inst_3 = []

    wout_pipe_inst_0 = []
    wout_pipe_inst_1 = []
    wout_pipe_inst_2 = []
    wout_pipe_inst_3 = []
    wout_pipe_inst_4 = []
    wout_pipe_inst_5 = []
    wout_pipe_inst_6 = []
    wout_pipe_inst_7 = []
    wout_pipe_inst_8 = []


    weigths_in_pipe_inst = []

    for i in range(0, 9):
        wout_pipe_inst_0.append(Register(clk, wout_pipe_0[i], wout_pipe_1[i]))
        wout_pipe_inst_1.append(Register(clk, wout_pipe_1[i], wout_pipe_2[i]))
        wout_pipe_inst_2.append(Register(clk, wout_pipe_2[i], wout_pipe_3[i]))
        wout_pipe_inst_3.append(Register(clk, wout_pipe_3[i], wout_pipe_4[i]))
        wout_pipe_inst_4.append(Register(clk, wout_pipe_4[i], wout_pipe_5[i]))
        wout_pipe_inst_5.append(Register(clk, wout_pipe_5[i], wout_pipe_6[i]))
        wout_pipe_inst_6.append(Register(clk, wout_pipe_6[i], wout_pipe_7[i]))
        wout_pipe_inst_7.append(Register(clk, wout_pipe_7[i], wout_pipe_8[i]))
        wout_pipe_inst_8.append(Register(clk, wout_pipe_8[i], wout_pipe_9[i]))

        win_pipe_inst_0.append(Register(clk, win[i],        win_pipe_0[i]))
        win_pipe_inst_1.append(Register(clk, win_pipe_0[i], win_pipe_1[i]))
        win_pipe_inst_2.append(Register(clk, win_pipe_1[i], win_pipe_2[i]))
        win_pipe_inst_3.append(Register(clk, win_pipe_2[i], win_pipe_3[i]))

        weigths_in_pipe_inst.append(Register(clk, weights_in[i], weigths_in_pipe_0[i]))
        weigths_in_pipe_inst.append(Register(clk, weigths_in_pipe_0[i], weigths_in_pipe_1[i]))
        weigths_in_pipe_inst.append(Register(clk, weigths_in_pipe_1[i], weigths_in_pipe_2[i]))
        weigths_in_pipe_inst.append(Register(clk, weigths_in_pipe_2[i], weigths_in_pipe_3[i]))
        weigths_in_pipe_inst.append(Register(clk, weigths_in_pipe_3[i], weigths_in_pipe_4[i]))
        weigths_in_pipe_inst.append(Register(clk, weigths_in_pipe_4[i], weigths_in_pipe_5[i]))
        weigths_in_pipe_inst.append(Register(clk, weigths_in_pipe_5[i], weigths_in_pipe_6[i]))
        weigths_in_pipe_inst.append(Register(clk, weigths_in_pipe_6[i], weigths_in_pipe_7[i]))
        weigths_in_pipe_inst.append(Register(clk, weigths_in_pipe_7[i], weigths_in_pipe_8[i]))
        weigths_in_pipe_inst.append(Register(clk, weigths_in_pipe_8[i], weigths_in_pipe_9[i]))
        weigths_in_pipe_inst.append(Register(clk, weigths_in_pipe_9[i], weigths_in_pipe_10[i]))
        weigths_in_pipe_inst.append(Register(clk, weigths_in_pipe_10[i], weigths_in_pipe_11[i]))
        weigths_in_pipe_inst.append(Register(clk, weigths_in_pipe_11[i], weigths_in_pipe_12[i]))


    w_est_int_0 = WeightsEstimate(clk,
                                  mean,
                                  win[0], win[1], win[2], win[3], win[4], win[5], win[6], win[7], win[8],
                                  wout_pipe_0[0], wout_pipe_0[1], wout_pipe_0[2], wout_pipe_0[3], wout_pipe_0[4], wout_pipe_0[5], wout_pipe_0[6], wout_pipe_0[7], wout_pipe_0[8])

    # pipeline for old mean value
    mean_pipe_0 = [Signal(modbv(1, min=mean.min, max=mean.max)) for _ in range(10)]
    mean_pipe_regs_inst_0 = []
    mean_pipe_regs_inst_0.append(Register(clk, mean, mean_pipe_0[9]))

    for i in range(0, 9):
        mean_pipe_regs_inst_0.append(Register(clk, mean_pipe_0[i+1], mean_pipe_0[i]))

    wmean_inst_0 = WMean(clk,
                         win_pipe_3[0], win_pipe_3[1], win_pipe_3[2], win_pipe_3[3], win_pipe_3[4], win_pipe_3[5], win_pipe_3[6], win_pipe_3[7], win_pipe_3[8],
                         wout_pipe_0[0], wout_pipe_0[1], wout_pipe_0[2], wout_pipe_0[3], wout_pipe_0[4], wout_pipe_0[5], wout_pipe_0[6], wout_pipe_0[7], wout_pipe_0[8],
                         wmean)

    mean_diff_inst_0 = wmean_diff(clk, mean_pipe_0[0], wmean, bypass_0)

    wmean_pipe_0 = [Signal(modbv(1, min=mean.min, max=mean.max)) for _ in range(4)]
    wmean_pipe_reg_0 = Register(clk, wmean, wmean_pipe_0[0])
    wmean_pipe_reg_1 = Register(clk, wmean_pipe_0[0], wmean_pipe_0[1])
    wmean_pipe_reg_2 = Register(clk, wmean_pipe_0[1], wmean_pipe_0[2])
    wmean_pipe_reg_3 = Register(clk, wmean_pipe_0[2], new_mean)

    @always(clk.posedge)
    def BypassLogic():
        bypass.next = bypass_0 or bypass_pipe_0[0]

        if bypass_pipe_0[0]:
            wout0.next = weigths_in_pipe_12[0]
            wout1.next = weigths_in_pipe_12[1]
            wout2.next = weigths_in_pipe_12[2]
            wout3.next = weigths_in_pipe_12[3]
            wout4.next = weigths_in_pipe_12[4]
            wout5.next = weigths_in_pipe_12[5]
            wout6.next = weigths_in_pipe_12[6]
            wout7.next = weigths_in_pipe_12[7]
            wout8.next = weigths_in_pipe_12[8]
        else:
            wout0.next = wout_pipe_9[0]
            wout1.next = wout_pipe_9[1]
            wout2.next = wout_pipe_9[2]
            wout3.next = wout_pipe_9[3]
            wout4.next = wout_pipe_9[4]
            wout5.next = wout_pipe_9[5]
            wout6.next = wout_pipe_9[6]
            wout7.next = wout_pipe_9[7]
            wout8.next = wout_pipe_9[8]



    return instances()


def Sub2(clk, a, b, q, nq, sign):

    @always(clk.posedge)
    def SubLogic():
        sub = modbv(0, min=-2**32, max=2**32)
        sub[:] = (a << 16) - b
        q.next = sub
        sign.next = sub[31]
        nq.next = b - (a << 16)

    return SubLogic


if __name__ == "__main__":

    # clk = Signal(bool(0))
    # wmean = Signal(intbv(0)[32:])
    # deviation = Signal(intbv(0)[16:])
    #
    # x = [Signal(modbv(0x00010000)[32:]) for _ in range(9)]
    # w = [Signal(modbv(0x00010000)[32:]) for _ in range(9)]
    #
    # inst = toVHDL(WMean, clk,
    #               x[0], x[1], x[2], x[3], x[4], x[5], x[6], x[7], x[8],
    #               w[0], w[1], w[2], w[3], w[4], w[5], w[6], w[7], w[8],
    #               wmean)


    # clk = Signal(bool(0))
    # wmean = Signal(intbv(0)[32:])
    # deviation = Signal(intbv(0)[16:])
    #
    # x = [Signal(modbv(0x00010000)[32:]) for _ in range(9)]
    # w = [Signal(modbv(0x00010000)[32:]) for _ in range(9)]
    #
    # inst = toVHDL(Deviation, clk,
    #               w[0], w[1], w[2], w[3], w[4], w[5], w[6], w[7], w[8],
    #               x[0], x[1], x[2], x[3], x[4], x[5], x[6], x[7], x[8],
    #               wmean,
    #               deviation)


    # clk = Signal(bool(0))
    # s = Signal(bool(0))
    #
    # wmean = Signal(intbv(0)[32:])
    # deviation = Signal(intbv(0)[16:])
    #
    # x = [Signal(modbv(0x00010000)[32:]) for _ in range(9)]
    # w = [Signal(modbv(0x00010000)[32:]) for _ in range(9)]
    #
    # inst = toVHDL(WeightsEstimate, clk,
    #               wmean,
    #               x[0], x[1], x[2], x[3], x[4], x[5], x[6], x[7], x[8],
    #               w[0], w[1], w[2], w[3], w[4], w[5], w[6], w[7], w[8])


    clock = Signal(bool(0))

    x = [Signal(intbv(0, min=0, max=2**8)) for _ in range(9)]
    w = [Signal(modbv(0)[32:]) for _ in range(9)]

    wout = [Signal(modbv(0)[32:]) for _ in range(9)]

    bypass = Signal(bool(0))
    bypass_in = Signal(bool(0))

    wmean = Signal(intbv(0, min=0, max=2**32))
    wmean_new = Signal(modbv(0, min=0, max=2**32))

    inst = toVHDL(loop_block,
                  clock,
                  wmean,
                  bypass_in,
                  w[0], w[1], w[2], w[3], w[4], w[5], w[6], w[7], w[8],
                  x[0], x[1], x[2], x[3], x[4], x[5], x[6], x[7], x[8],
                  wout[0], wout[1], wout[2], wout[3], wout[4], wout[5], wout[6], wout[7], wout[8],
                  wmean_new,
                  bypass)

# def loop_block(clk,
#                mean,
#                bypass_in,
#                w0, w1, w2, w3, w4, w5, w6, w7, w8,
#                win0, win1, win2, win3, win4, win5, win6, win7, win8,
#                wout0, wout1, wout2, wout3, wout4, wout5, wout6, wout7, wout8,
#                new_mean,
#                bypass):