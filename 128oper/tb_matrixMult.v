module tb_matrixMult;

reg clk;
reg [4095:0] vector;
wire [4095:0] result;

initial begin
    $from_myhdl(
        clk,
        vector
    );
    $to_myhdl(
        result
    );
end

matrixMult dut(
    clk,
    vector,
    result
);

endmodule
