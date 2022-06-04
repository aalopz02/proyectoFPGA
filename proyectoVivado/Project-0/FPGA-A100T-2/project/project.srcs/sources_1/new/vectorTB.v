`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 04/18/2022 03:05:34 PM
// Design Name: 
// Module Name: vectorTB
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


module vectorTB();
    
    parameter HALF_PERIOD = 10;
    reg clk = 0;
    always #HALF_PERIOD clk=~clk;
    
    reg [64-1:0] vectorIn = 64'h0102030405060708;
    wire [64-1:0] vectorOut;
    
    
    vectorTest VT(
        clk,
        vectorIn,
        vectorOut
    );
    
    initial begin
        #HALF_PERIOD;
        #HALF_PERIOD;
        #HALF_PERIOD;
        #HALF_PERIOD;
    end
    
endmodule
