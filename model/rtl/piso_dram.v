
`include "/home/Workspace/seba/frb_actual/includes.v"
module piso_dram #(
    parameter INPUT_SIZE = 288,
    parameter OUTPUT_SIZE = 8
)
(
    input wire clk,
    input wire ce,
    input wire rst,
    //stupid matlab
    //input wire [INPUT_SIZE-1:0] i_parallel,
    //output wire [OUTPUT_SIZE-1:0] o_serial,
    input wire [287:0] i_parallel,
    output wire [7:0] o_serial,

    input wire      fifo_empty,
    output wire     fifo_re,

    output wire     valid
);

// module that interface a fifo that contains parallel data
//that we wish to serialize.
//note that for each value that we read from the fifo we need 
// INPUT_SIZE/OUTPUT_SIZE cycles until we could read the next val


//fucking sysgen
//parameter CYCLES_BTW = INPUT_SIZE/OUTPUT_SIZE; 

//parameter IDLE = 2'b0;
//parameter BUSY = 2'b1;
localparam CYCLES_BTW = INPUT_SIZE/OUTPUT_SIZE; 
localparam IDLE = 2'b0;
localparam BUSY = 2'b1;


reg [$clog2(CYCLES_BTW)-1:0] counter=0;
reg re=0, valid_r=0; //read enable and valid..

reg state=IDLE, next_state=IDLE;


always@(posedge clk)begin
    if(rst)
        state <= IDLE;
    else
        state <= next_state;
end


always@(*)begin
    case(state)
        IDLE:   begin
            if(~fifo_empty)     next_state = BUSY;
            else                next_state = IDLE;
        end
        BUSY:   begin
            if(counter==(CYCLES_BTW)-1) next_state = IDLE;
            else                        next_state = BUSY;
        end
    endcase 
end

always@(posedge clk)begin
    case(state)
        IDLE: begin
            counter<=0;
            valid_r <= 0;
        end
        BUSY: begin
            valid_r<= 1;
            if(counter==(CYCLES_BTW)-1)
                counter <=0;
            else
                counter <= counter +1;
        end
    endcase
end


always@(posedge clk)begin
    re = ~state && next_state && ~rst;
end

//detect the transition of states
assign fifo_re = re; 


reg [OUTPUT_SIZE-1:0] serial_out=0;

/*
always@(*)begin
    case(counter)
        1: serial_out = i_parallel[OUTPUT_SIZE-1:0];
        2: serial_out = i_parallel[2*OUTPUT_SIZE-1:1*OUTPUT_SIZE];
        3: serial_out = i_parallel[3*OUTPUT_SIZE-1:2*OUTPUT_SIZE];
        0: serial_out = i_parallel[4*OUTPUT_SIZE-1:3*OUTPUT_SIZE];
    endcase
end
*/


always@(posedge clk)begin
    case(counter)
        1: serial_out = i_parallel[OUTPUT_SIZE-1:0];   
        2: serial_out = i_parallel[2*OUTPUT_SIZE-1:1*OUTPUT_SIZE];
        3: serial_out = i_parallel[3*OUTPUT_SIZE-1:2*OUTPUT_SIZE];
        4: serial_out = i_parallel[4*OUTPUT_SIZE-1:3*OUTPUT_SIZE];
        5: serial_out = i_parallel[5*OUTPUT_SIZE-1:4*OUTPUT_SIZE];
        6: serial_out = i_parallel[6*OUTPUT_SIZE-1:5*OUTPUT_SIZE];
        7: serial_out = i_parallel[7*OUTPUT_SIZE-1:6*OUTPUT_SIZE];
        8: serial_out = i_parallel[8*OUTPUT_SIZE-1:7*OUTPUT_SIZE];
        9: serial_out = i_parallel[9*OUTPUT_SIZE-1:8*OUTPUT_SIZE];
        10: serial_out = i_parallel[10*OUTPUT_SIZE-1:9*OUTPUT_SIZE];
        11: serial_out = i_parallel[11*OUTPUT_SIZE-1:10*OUTPUT_SIZE];
        12: serial_out = i_parallel[12*OUTPUT_SIZE-1:11*OUTPUT_SIZE];
        13: serial_out = i_parallel[13*OUTPUT_SIZE-1:12*OUTPUT_SIZE];
        14: serial_out = i_parallel[14*OUTPUT_SIZE-1:13*OUTPUT_SIZE];
        15: serial_out = i_parallel[15*OUTPUT_SIZE-1:14*OUTPUT_SIZE];
        
        16: serial_out = i_parallel[16*OUTPUT_SIZE-1:15*OUTPUT_SIZE];
        17: serial_out = i_parallel[17*OUTPUT_SIZE-1:16*OUTPUT_SIZE];
        18: serial_out = i_parallel[18*OUTPUT_SIZE-1:17*OUTPUT_SIZE];
        19: serial_out = i_parallel[19*OUTPUT_SIZE-1:18*OUTPUT_SIZE];
        20: serial_out = i_parallel[20*OUTPUT_SIZE-1:19*OUTPUT_SIZE];
        21: serial_out = i_parallel[21*OUTPUT_SIZE-1:20*OUTPUT_SIZE];
        22: serial_out = i_parallel[22*OUTPUT_SIZE-1:21*OUTPUT_SIZE];
        23: serial_out = i_parallel[23*OUTPUT_SIZE-1:22*OUTPUT_SIZE];
        24: serial_out = i_parallel[24*OUTPUT_SIZE-1:23*OUTPUT_SIZE];
        25: serial_out = i_parallel[25*OUTPUT_SIZE-1:24*OUTPUT_SIZE];
        26: serial_out = i_parallel[26*OUTPUT_SIZE-1:25*OUTPUT_SIZE];
        27: serial_out = i_parallel[27*OUTPUT_SIZE-1:26*OUTPUT_SIZE];
        28: serial_out = i_parallel[28*OUTPUT_SIZE-1:27*OUTPUT_SIZE];
        29: serial_out = i_parallel[29*OUTPUT_SIZE-1:28*OUTPUT_SIZE];
        30: serial_out = i_parallel[30*OUTPUT_SIZE-1:29*OUTPUT_SIZE];
        31: serial_out = i_parallel[31*OUTPUT_SIZE-1:30*OUTPUT_SIZE];
        32: serial_out = i_parallel[32*OUTPUT_SIZE-1:31*OUTPUT_SIZE];
        33: serial_out = i_parallel[33*OUTPUT_SIZE-1:32*OUTPUT_SIZE];
        34: serial_out = i_parallel[34*OUTPUT_SIZE-1:33*OUTPUT_SIZE];
        35: serial_out = i_parallel[35*OUTPUT_SIZE-1:34*OUTPUT_SIZE];
        0: serial_out = i_parallel[36*OUTPUT_SIZE-1:35*OUTPUT_SIZE];
    endcase
end

/*
always@(*)begin
    integer i;
    for(i=0; i<CYCLES_BTW;i=i+1)begin: loop
        if(counter==i)begin
            serial_out = i_parallel[(i+1)*OUTPUT_SIZE-1:i*OUTPUT_SIZE];
        end
    end
end
*/

//just lookin at the traces, we need a delay in the valid signal
reg valid_delay=0;
always@(posedge clk)begin
    valid_delay = valid_r;
end


assign valid = valid_delay;//valid_r;
assign o_serial = serial_out; 
endmodule 
