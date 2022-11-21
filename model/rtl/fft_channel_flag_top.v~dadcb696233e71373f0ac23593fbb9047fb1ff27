`include "/home/Workspace/seba/arte_debug/v6/rtl/includes.v"

module fft_chann_flag_top (
    input wire clk,
    input wire ce,
    input wire sync_in,
    input wire [143:0] din,
    output wire sync_out,
    output wire [143:0] dout,
    //config
    input wire [31:0] config_flag,
    input wire [31:0] config_num,
    input wire config_en
);



fft_chann_flag #(
    .STREAMS(4),
    .FFT_SIZE(2048),
    .DIN_WIDTH(36)
) fft_chann_flag_inst (
    .clk(clk),
    .sync_in(sync_in),
    .din(din),
    .sync_out(sync_out),
    .dout(dout),
    .config_flag(config_flag),
    .config_num(config_num),
    .config_en(config_en)
);


endmodule
