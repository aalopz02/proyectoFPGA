`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 04/18/2022 01:07:17 PM
// Design Name: 
// Module Name: vectorTest
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


module vectorTest #(parameter OP_WIDTH = 32, parameter WINDOW = 8)(
    input clk,
    input [(OP_WIDTH*WINDOW)-1:0] vectorIn,
    output [(OP_WIDTH*WINDOW)-1:0] vectorOut
    );
    
    reg [(OP_WIDTH*WINDOW)-1:0] vectorAux = 0;
    
    integer i;
    always @ (posedge clk) begin
        for (i =0; i < WINDOW;i = i + 1) begin
            vectorAux[OP_WIDTH*i +: OP_WIDTH] <= vectorIn[OP_WIDTH*i +: OP_WIDTH] + vectorIn[OP_WIDTH*i +: OP_WIDTH];
        end
    end
    
    assign vectorOut = vectorAux;
    
endmodule
