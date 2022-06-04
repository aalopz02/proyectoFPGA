`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 04/14/2022 12:58:10 PM
// Design Name: 
// Module Name: ControlModule
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


module ControlModule #(parameter OP_WIDTH = 32, parameter WINDOW = 8)(
    input clk,
    input [31:0] data,
    output reg [31:0] dataOut,
    output led1,
    output led2,
    output led3,
    output enableDoOper,
    output [(OP_WIDTH*WINDOW)-1:0] vectorOutToOper,
    input [(OP_WIDTH*WINDOW)-1:0] vectorResult
);

    parameter init_state = 3'd0;
    parameter buffer_state = 3'd1;
    parameter calc_state = 3'd2;
    parameter done_state = 3'd3;
    parameter return_state = 3'd4;
    parameter pause_state = 3'd5;
    parameter restart_state = 3'd6;
    parameter doneReturn_state = 3'd7;

    reg [2:0] current_state = 3'b000;
    reg [2:0] next_state = 3'b000;
    reg [2:0] prev_state;

    parameter cmd_start = 16'd1;
    parameter cmd_stop = 16'd2;
    parameter cmd_restart = 16'd3;
    parameter cmd_ready = 16'd4;
    parameter cmd_take_nextRe = 16'd5;
    parameter cmd_take_nextIm = 16'd6;
    parameter cmd_need_next = 16'd7;
    parameter cmd_resume = 16'd8;

    parameter calc_min_cycles = (WINDOW*2)-1;
    reg [15:0] calc_cycles = 15'd0;
    
    integer vectorFillCount = 0;
    integer vectorPullCount = 0;
    integer idxFill = 0;
    integer idxPull = 0;
    
    wire [15:0] data_cmd;
    wire [15:0] data_value;

    reg expectingRe = 1;
    reg returning = 1;

    reg [15:0] dataInRe;
    reg [31:0] dataOutAux;
    
    reg [31:0] vectorAux [7:0];
    reg [31:0] vectorOutToPC [7:0];
    
    reg [(OP_WIDTH*WINDOW)-1:0] vectorOutAux;
    
    assign led1 = ~current_state[0];
    assign led2 = ~current_state[1];
    assign led3 = ~current_state[2];

    assign data_cmd = data[15:0];
    assign data_value = data[31:16];

    assign vectorOutToOper = vectorOutAux;
    assign enableDoOper = (current_state == calc_state) ? 1'b0 : 1'b1;

    always @ (posedge clk) begin
        case (current_state)
            init_state: begin
                if (data_cmd == cmd_start) begin
                    next_state <= buffer_state;
                    vectorFillCount <= 0;
                    expectingRe <= 1'b1;
                    dataOut <= 32'h79646572;//redy
                end
            end
            buffer_state: begin
                if (data_cmd == cmd_take_nextRe &&  expectingRe == 1'b1) begin
                    vectorAux[vectorFillCount][31:16] = data_value;
                    expectingRe = 1'b0;
                    dataOut = 32'h65526B6F;//okRe
                end
                else if (data_cmd == cmd_take_nextIm && expectingRe == 1'b0) begin
                    if (vectorFillCount == WINDOW) begin
                        vectorFillCount <= 0;
                        expectingRe <= 1'b1;
                        next_state <= calc_state;
                        for (idxFill =0; idxFill < WINDOW;idxFill = idxFill + 1) begin
                            vectorOutAux[OP_WIDTH*idxFill +: OP_WIDTH] <= vectorAux[idxFill];
                        end
                        calc_cycles <= 15'd0;
                    end
                    else begin
                        vectorAux[vectorFillCount][15:0] = data_value;
                        vectorFillCount = vectorFillCount + 1;
                        expectingRe = 1'b1;
                        dataOut = 32'h6D496B6F;//okIm
                    end
                end
            end
            calc_state: begin
                if (data_cmd == cmd_stop) begin
                    next_state <= pause_state;
                    prev_state <= calc_state;
                end
                else begin
                    if (calc_cycles >= calc_min_cycles) begin
                        next_state <= done_state;
                    end
                    else begin
                        calc_cycles <= calc_cycles + 15'd1;
                    end
                end
            end
            done_state: begin
                if (data_cmd == cmd_ready) begin
                    next_state <= return_state;
                    returning <= 1'b1;
                    vectorPullCount <= 0;
                    dataOut <= 32'h00006B6F;
                end
                else begin
                    dataOut <= 32'h656E6F64;//done
                end
            end
            return_state: begin
                if (data_cmd == cmd_need_next && returning == 1'b1) begin
                    if (vectorPullCount >= WINDOW) begin
                        vectorPullCount <= 0;
                        next_state <= doneReturn_state;
                        dataOut <= 32'h656E6F64;
                    end
                    else begin
                        dataOut <= vectorOutToPC[vectorPullCount];
                        returning <= 1'b0;
                    end
                end
                else if (data_cmd == cmd_ready && returning == 1'b0) begin
                    vectorPullCount <= vectorPullCount + 1;
                    returning <= 1'b1;
                end
            end
            doneReturn_state: begin
                if (data_cmd == cmd_start) begin
                    next_state <= buffer_state;
                    dataOut <= 32'h79646572;//redy
                end
                else if (data_cmd == cmd_stop) begin
                    prev_state <= doneReturn_state;
                    next_state <= pause_state;
                end
                else begin
                    dataOut <= 32'h656E6F64;
                end
            end
            pause_state: begin
                dataOut[15:0] <= 16'h3A70;
                dataOut[23:16] <= 8'h30; 
                dataOut[31:27] <= 5'b00110;
                dataOut[26:24] <= prev_state;
                if (data_cmd == cmd_resume) begin
                    next_state <= prev_state;
                end
                else if (data_cmd == cmd_restart) begin
                    next_state <= restart_state;
                end
            end
            restart_state: begin
                next_state <= init_state;
            end
        endcase
    end

    always @ (negedge clk) begin
        current_state <= next_state;
        if (next_state == done_state) begin
            for (idxPull =0; idxPull < WINDOW;idxPull = idxPull + 1) begin
                vectorOutToPC[idxPull] <= vectorResult[OP_WIDTH*idxPull +: OP_WIDTH];
            end
        end
    end

endmodule
