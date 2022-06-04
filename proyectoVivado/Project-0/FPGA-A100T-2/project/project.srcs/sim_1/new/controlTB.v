`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 04/18/2022 11:11:21 AM
// Design Name: 
// Module Name: controlTB
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////


module controlTB();
    
    parameter HALF_PERIOD = 10;
    reg clk = 0;
    always #HALF_PERIOD clk=~clk;
    
    reg [31:0] data = 32'd0;
    wire [31:0] dataOut;
    
    wire enableDoOper;
    wire enableFill;
    
    wire [255:0] vector;
    
    wire [2:0] state; 
    
    
    ControlModule cm(
     clk,
     data,
     dataOut,
     state[0],
     state[1],
     state[2],
     enableDoOper,
     enableFill,
     vector);
    
    
    initial begin
    
        #HALF_PERIOD;
        data = 32'h00000001;
        #HALF_PERIOD;
        #HALF_PERIOD;
        data = 32'h01000005;
        #HALF_PERIOD;
        #HALF_PERIOD;
        data = 32'h01000006;
        #HALF_PERIOD;
        #HALF_PERIOD;
        data = 32'h02000005;
        #HALF_PERIOD;
        #HALF_PERIOD;
        data = 32'h02000006;
        #HALF_PERIOD;
        #HALF_PERIOD;
        data = 32'h12340005;
        #HALF_PERIOD;
        #HALF_PERIOD;
        data = 32'h56780006;
        #HALF_PERIOD;
        #HALF_PERIOD;
        data = 32'h01010005;
        #HALF_PERIOD;
        #HALF_PERIOD;
        data = 32'h01010006;
        #HALF_PERIOD;
        #HALF_PERIOD;
        data = 32'h02020005;
        #HALF_PERIOD;
        #HALF_PERIOD;
        data = 32'h02020006;
        #HALF_PERIOD;
        #HALF_PERIOD;
        data = 32'h02020005;
        #HALF_PERIOD;
        #HALF_PERIOD;
        data = 32'h02020006;
        #HALF_PERIOD;
        #HALF_PERIOD;
        data = 32'h02020005;
        #HALF_PERIOD;
        #HALF_PERIOD;
        data = 32'h02020006;
        #HALF_PERIOD;
        #HALF_PERIOD;
        data = 32'h02020005;
        #HALF_PERIOD;
        #HALF_PERIOD;
        data = 32'h02020006;
        #HALF_PERIOD;
        #HALF_PERIOD;
        data = 32'h02020005;
        #HALF_PERIOD;
        #HALF_PERIOD;
        data = 32'h02020006;
        #HALF_PERIOD;
        #HALF_PERIOD;
        #HALF_PERIOD;
        #HALF_PERIOD;
        data = 32'h00000004;
        #HALF_PERIOD;
        #HALF_PERIOD;
        data = 32'h00000007;
        #HALF_PERIOD;
        #HALF_PERIOD;
        data = 32'h00000007;
        #HALF_PERIOD;
        #HALF_PERIOD;
        data = 32'h00000007;
        #HALF_PERIOD;
        #HALF_PERIOD;
        data = 32'h00000007;
        #HALF_PERIOD;
        #HALF_PERIOD;
        
        
    end
endmodule
