`include "/home/Workspace/seba/arte_debug/v6/rtl/includes.v"

module moving_average_top
 (
    input wire clk,
    input wire ce,
    input wire rst,
    input wire signed [24:0] din,
    input wire din_valid,
    output wire signed [24:0] dout,
    output wire dout_valid
);

moving_average #(
    .DIN_WIDTH(25),
    .DIN_POINT(24),
    .WINDOW_LEN(128),
    .DOUT_WIDTH(25),
    .APPROX("truncate")
) mov_avg_inst (
    .clk(clk),
    .rst(rst),
    .din(din),
    .din_valid(din_valid),
    .dout(dout),
    .dout_valid(dout_valid)
);

endmodule
