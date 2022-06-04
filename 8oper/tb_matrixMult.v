module tb_matrixMult;

reg clk;
reg [255:0] vector;
wire [255:0] result;

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
