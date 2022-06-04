module tb_matrixMult;

reg [4095:0] vector = 4096'h0102030405060708;
wire [4095:0] result;

parameter HALF_PERIOD = 10;
reg clk = 0;
always #HALF_PERIOD clk=~clk;

    
    matrixMult dut(
    clk,
    vector,
    result
);

    initial begin
        #HALF_PERIOD;
        #HALF_PERIOD;
        #HALF_PERIOD;
        #HALF_PERIOD;
    end



endmodule
