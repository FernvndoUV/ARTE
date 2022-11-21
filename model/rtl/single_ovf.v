
module single_ovf#(
    parameter DIN_WIDTH = 8
) (
    input wire clk,
    input wire rst,
    input wire [DIN_WIDTH-1:0] din,

    output wire clip
);

reg ovf=0;
always@(posedge clk)begin
    if(rst)
        ovf <=0;
    else if(din[DIN_WIDTH-1] & (&(~din[DIN_WIDTH-2:0])))
        ovf <= 1;
    else if(~din[DIN_WIDTH-1] & (&din[DIN_WIDTH-2:0]))
        ovf <= 1;
end

assign clip = ovf;


endmodule
