%%  Author: Sebastian Jorquera

%always check the fft/unscramble to set the reorder 
%parameter in the sync_gen! we set a dictionary like obj to save some
%sync values

model_name = 'arte';
bw = 600;           %mhz
fft_size = 12;      %to change it you have to modify the ngc also and change the black boxes

%%parameters

%delay prog
del_prog_max_delay = 128;
del_prog_bram_type = 'Dual Port';   %'Dual Port' or 'Single Port'
del_prog_bram_lat = 2;              %

%pre pfb delay
pre_pfb_delay = 1;

%snapshot
snap_samples = 10;

%post fft delay
post_fft_delay = 3;


%antenna power
pow_add_lat = 2;
pow_mult_lat = 3;

%the power is calculated full scale then you could reduce it
pow_shift = 13;  %left shift
pow_resize = 20;
pow_point = 19;

%accumulator output
acc_out = 32;   %only could be 8,16,32,64,128 to match the brams


%pre bram delay
antenna_pre_bram_delay = 2;

%beam post complex adding 
post_complex_add_dly =3;

%%This part is for the generate the spectrum that goes into the 10gbe

%beam power latencies
beam_pow_add_lat = 2;
beam_pow_mul_lat = 3;

%power convert
beam_pow_conv_shift = 15;
beam_pow_width = 16;
beam_pow_point = 15;

%post acc latency
beam_post_acc_lat = 2;

%%

%%flag channels stuffs..
%but this goes into the dedispersors blocks so take that in mind
%post flag
post_flag_delay = 3;

%post flag power
flag_power_add_lat = 2;
flag_power_mul_lat = 3;

%flag convert
flag_conv_width = 16;
flag_conv_point = 15;
flag_conv_shift = 15;


%%
%Dedispersor stuffs
%at the end of the last section we have an adder tree and then we add 8
%channels so we have a data with: flag_conv_width+5 and we want to convert
%it.. so you are warned
dedispersor_num = 1;

dedisp_acc_in_shift = 0;
dedisp_acc_in_width = 16;
dedisp_acc_in_point = 10;

dedisp_acc_out_width = 20;

%pre dedisp conv
dedisp_in_width = 20;
dedisp_in_point = 10;
dedisp_in_shift = 0;

%pre dedisp delay
pre_dedisp_delay = 2;

%dedispersor output (integrated)
dedsip_out_width = 20;        %the point here is the same as the input

post_dedisp_shift = 0;
post_dedisp_width = 20;
post_dedisp_point = 10;

post_dedisp_delay = 1;


%mov avg parameters
mov_avg_window = 128;



%% RFI stuffs

beam_rfi_delay = 3;
beam_rfi_shift = 9;
beam_rfi_width = 9;
beam_rfi_point = 8;

 %delay comes from complex add, post_complex_delay, flaging, and the beam flag
rfi_delay = 2+post_complex_add_dly+1+beam_rfi_delay;   
rfi_shift =  beam_rfi_shift;
rfi_width = beam_rfi_width;
rfi_point = beam_rfi_point;


%RFI correlator
%check the dout widths of the corr and the pow!!!

rfi_corr_cmult_width = 18;  %%the input is 2*rfi_width_2*rfi_point
rfi_corr_cmult_point = 16;
rfi_corr_cmult_add_dly = 2;
rfi_corr_cmult_mult_dly = 3;
rfi_corr_post_cmult_dly = 1;
rfi_corr_acc_width = 32;
rfi_corr_post_acc_dly = 2;
rfi_corr_pow_add_dly = 2;
rfi_corr_pow_mult_dly = 3;
rfi_corr_dout_shift = 11;    %%the input is acc_width, cmult_point
rfi_corr_dout_width = 16;
rfi_corr_dout_point = 2;

%RFI power ... it should be in sync with the correlator
rfi_pow_pow_add_dly = rfi_corr_pow_add_dly;
rfi_pow_pow_mult_dly = rfi_corr_pow_mult_dly;
rfi_pow_post_pow_dly = rfi_corr_post_cmult_dly;
rfi_pow_acc_width = 32;
rfi_pow_post_acc_dly = rfi_corr_post_acc_dly;

rfi_pow_post_acc_shift = 0;     %%the input is 2*rfi_width_2*rfi_point
rfi_pow_post_acc_conv_width = 32;
rfi_pow_post_acc_conv_point = 16;
rfi_pow_dout_shift = 11;
rfi_pow_dout_width = 16;
rfi_pow_dout_point = 2;
rfi_pow_cmult_add_dly = rfi_corr_cmult_add_dly;
rfi_pow_cmult_mult_dly = rfi_corr_cmult_mult_dly;



%rfi phase
rfi_phase_din_delay = 2;
rfi_phase_din_width = rfi_corr_dout_width; 
rfi_phase_din_point = rfi_corr_dout_point;
rfi_pre_cordic_width = rfi_corr_dout_width;
rfi_pre_cordic_point = rfi_corr_dout_point;
rfi_cordic_iters = 16;






%% 
fft_vals =          {7,8,9,10,11,12,13,14,15,16,17};
unscramble_values = [2,5,3, 7, 4, 9, 5,11, 6,13, 7];
reorder_vals = containers.Map(fft_vals, unscramble_values);
%%

disp(['This bw needs a fpga clk:', num2str(bw/4)]);

%write adc clock and fpga clock
disp('Writing adc and fpga clocks');
adc0_name = strcat(model_name, '/asiaa_adc5g0');
adc1_name = strcat(model_name, '/asiaa_adc5g1');
xsg_name = strcat(model_name, '/XSG_core_config');

set_param(adc0_name, 'adc_clk_rate', num2str(2*bw));
set_param(adc1_name, 'adc_clk_rate', num2str(2*bw));
set_param(xsg_name, 'clk_rate', num2str(bw/4));

%write delay programable
disp('Writing programmable delay wideband');
for i = (0:1:2)
    name = strcat(model_name, '/delay_wideband_prog', int2str(i));
    set_param(name, 'max_delay', int2str(del_prog_max_delay ));
    set_param(name, 'bram_type', del_prog_bram_type);
    set_param(name, 'bram_latency', int2str(del_prog_bram_lat));
end


%write delay pre pfb
disp('Write snapshots');
for i = (1:1:3)
    name = strcat(model_name, '/pre_pfb_delay', int2str(i));
    set_param(name, 'lat', int2str(pre_pfb_delay))
end

%also set the delay in the 4 branch
set_param(strcat(model_name, '/delay_pre_pfb'), 'latency', int2str(pre_pfb_delay));

%write snapshots
for i = (0:1:3)
    name = strcat(model_name, '/adcsnap', int2str(i));
    set_param(name, 'nsamples', int2str(snap_samples));
end

%post fft delay
for i = (0:1:3)
    name = strcat(model_name, '/post_fft_delay', int2str(i));
    set_param(name, 'lat', int2str(post_fft_delay));
end

%antenas power
%fft power
disp('Update power blocks');
for i = (1:1:16)
   pow_name =  strcat(model_name, '/power',int2str(i));
   set_param(pow_name,'BitWidth', int2str(18))
   set_param(pow_name,'add_latency', int2str(pow_add_lat))
   set_param(pow_name,'mult_latency', int2str(pow_mult_lat))
end

%set the correspondant delay to sync the power
set_param(strcat(model_name, '/pipeline72'), 'latency', int2str(pow_add_lat+pow_mult_lat));
set_param(strcat(model_name, '/pipeline90'), 'latency', int2str(pow_add_lat+pow_mult_lat));
set_param(strcat(model_name, '/pipeline103'), 'latency', int2str(pow_add_lat+pow_mult_lat));
set_param(strcat(model_name, '/pipeline122'), 'latency', int2str(pow_add_lat+pow_mult_lat));


%convert power output
disp('Convert the output power');

for i=(0:1:3)
    pow_conv_name = strcat(model_name, '/power_convert', int2str(i));
    set_param(pow_conv_name, 'shift_val', int2str(pow_shift));
    set_param(pow_conv_name, 'conv_width', int2str(pow_resize));
    set_param(pow_conv_name, 'conv_point', int2str(pow_point));
end

%accumultors
disp('Update accumulators');
for i = (0:1:15)
   acc_name = strcat(model_name, '/simple_bram_vacc_0_', int2str(i));
   set_param(acc_name, 'vec_len', int2str(2^(fft_size-1-2)));
   set_param(acc_name, 'n_bits', int2str(acc_out));
   set_param(acc_name, 'bin_pt', int2str(pow_point));
end

%pre bram delay
disp('Set pre-brams delay');
for i = (0:1:3)
    name = strcat(model_name, '/pre_bram_delay', int2str(i));
    set_param(name, 'lat', int2str(antenna_pre_bram_delay));
end

%antennas brams
disp('Set antennas brams');
for i = (0:1:3)
    name = strcat(model_name, '/antenna_',int2str(i));
    set_param(name, 'data_width', int2str(4*acc_out))
end


%post complex adding delay
disp('Post complex adding delay');
name = strcat(model_name, '/beam_post_complex_add');
set_param(name, 'lat', int2str(post_complex_add_dly));


%% This part is the spectrum that goes into the 10gbe

%set beam power latencies
disp('Configure beam power blocks')
name = strcat(model_name, '/beam_power');
set_param(name, 'add_lat', int2str(beam_pow_add_lat));
set_param(name, 'mult_lat', int2str(beam_pow_mul_lat));

%set beam power 
disp('Convert beam power bitwidth');
name = strcat(model_name, '/beam_power_conv');
set_param(name, 'shift_val', int2str(beam_pow_conv_shift));
set_param(name, 'conv_width', int2str(beam_pow_width));
set_param(name, 'conv_point', int2str(beam_pow_point));

%set beam accs
disp('Configure beam accumulator');
for i =(0:1:3)
    name = strcat(model_name, '/beam_vacc', int2str(i));
    set_param(name, 'n_bits', int2str(32));
    set_param(name, 'bin_pt', int2str(beam_pow_point));
end

%set post accumualtion delay
disp('Set delay post beam accs');
name = strcat(model_name, '/beam_post_acc_delay');
set_param(name, 'lat', int2str(beam_post_acc_lat));

%% Flags


%%post flag stuffs
disp('Set delay post channel flag');
name = strcat(model_name, '/post_flag_delay');
set_param(name, 'lat', int2str(post_flag_delay));

%flag power
disp('Configure power of flagged spectrum');
name = strcat(model_name, '/flag_power');
set_param(name, 'add_lat', int2str(flag_power_add_lat));
set_param(name, 'mult_lat', int2str(flag_power_mul_lat));

%flag convert
disp('Configure flag convert');
name = strcat(model_name, '/flag_convert');
set_param(name, 'shift_val', int2str(flag_conv_shift));
set_param(name, 'conv_width', int2str(flag_conv_width));
set_param(name, 'conv_point', int2str(flag_conv_point));

%% Dedispersor stuffs

disp('Configure pre dedispersor vacc convert');
name = strcat(model_name, '/pre_dedisp_acc_conv');
set_param(name, 'shift_val', int2str(dedisp_acc_in_shift));
set_param(name, 'conv_width', int2str(dedisp_acc_in_width));
set_param(name, 'conv_point', int2str(dedisp_acc_in_point));

disp('Configure dedispersors accumulators');
for i=(0:1:(dedispersor_num-1))
   name = strcat(model_name, '/enabled_vacc',num2str(i));
   set_param(name, 'din_width', int2str(dedisp_acc_in_width));
   set_param(name, 'din_point', int2str(dedisp_acc_in_point));
   set_param(name, 'dout_width', int2str(dedisp_acc_out_width));
end


disp('Configure pre dedispersor convert');
for i=(0:1:(dedispersor_num-1))
    name = strcat(model_name, '/pre_dedisp_conv',num2str(i));
    set_param(name, 'shift_val', int2str(dedisp_in_shift));
    set_param(name, 'conv_width', int2str(dedisp_in_width));
    set_param(name, 'conv_point', int2str(dedisp_in_point));
end

disp('Configure pre dedisp delay')
for i=(0:1:(dedispersor_num-1))
    name = strcat(model_name, '/pre_dedisp_delay',num2str(i));
    set_param(name, 'lat', num2str(pre_dedisp_delay));
end

disp('Configure dedispersors')
for i=(0:1:(dedispersor_num-1))
    name = strcat(model_name, '/dedispersor', num2str(i));
    set_param(name, 'din_width', num2str(dedisp_in_width));
    set_param(name, 'din_point', num2str(dedisp_in_point));
    set_param(name, 'dout_width', num2str(dedsip_out_width));
    
    name = strcat(model_name, '/post_dedisp_conv', num2str(i));
    set_param(name, 'shift_val', int2str(post_dedisp_shift));
    set_param(name, 'conv_width', int2str(post_dedisp_width));
    set_param(name, 'conv_point', int2str(post_dedisp_point));
    
    name = strcat(model_name, '/post_dedisp_delay', num2str(i));
    set_param(name, 'lat', num2str(post_dedisp_delay));
end

disp('Configure mov avg');
for i=(0:1:(dedispersor_num-1))
    name = strcat(model_name, '/mov_avg', num2str(i));
    set_param(name, 'din_width', num2str(post_dedisp_width));
    set_param(name, 'din_point', num2str(post_dedisp_point));
    set_param(name, 'win_size', num2str(mov_avg_window));
end


disp('Configure threshold add')
for i=(0:1:(dedispersor_num-1))
    name = strcat(model_name, '/add_stat', num2str(i));
    set_param(name, 'n_bits', num2str(post_dedisp_width));
    set_param(name, 'bin_pt', num2str(post_dedisp_point));
end

%% RFI stuffs

%beam and reference antena data casting
disp('Configure Beam RFI delay and convert');
name = strcat(model_name, '/beam_rfi_delay');
set_param(name, 'lat', num2str(beam_rfi_delay));

name = strcat(model_name, '/beam_rfi_convert');
set_param(name, 'shift_val', num2str(beam_rfi_shift));
set_param(name, 'conv_width', num2str(beam_rfi_width));
set_param(name, 'conv_point', num2str(beam_rfi_point));

disp('Set the delays and datatype for the rfi antenna accordingly');
name = strcat(model_name, '/rfi_delay');
set_param(name, 'lat', num2str(rfi_delay));

name = strcat(model_name, '/rfi_convert');
set_param(name, 'shift_val', num2str(rfi_shift));
set_param(name, 'conv_width',num2str(rfi_width));
set_param(name, 'conv_point', num2str(rfi_point));


%rfi correlator
disp('Configuring RFI correlator');
name = strcat(model_name, '/rfi_correlator');
set_param(name, 'din_width', num2str(beam_rfi_width));
set_param(name, 'din_point', num2str(beam_rfi_point));
set_param(name, 'cmult_width', num2str(rfi_corr_cmult_width));
set_param(name, 'cmult_point', num2str(rfi_corr_cmult_point));
set_param(name, 'cmult_add_dly', num2str(rfi_corr_cmult_add_dly));
set_param(name, 'cmult_mult_dly', num2str(rfi_corr_cmult_mult_dly));
set_param(name, 'post_cmult_dly', num2str(rfi_corr_post_cmult_dly));
set_param(name, 'acc_width', num2str(rfi_corr_acc_width));
set_param(name, 'post_acc_dly', num2str(rfi_corr_post_acc_dly));
set_param(name, 'power_add_dly', num2str(rfi_corr_pow_add_dly));
set_param(name, 'power_mult_dly', num2str(rfi_corr_pow_mult_dly));
set_param(name, 'dout_shift', num2str(rfi_corr_dout_shift));
set_param(name, 'dout_width', num2str(rfi_corr_dout_width));
set_param(name, 'dout_point', num2str(rfi_corr_dout_point));


%rfi power
disp('Configuring RFI power')
name = strcat(model_name, '/rfi_power');
set_param(name, 'din_width', num2str(beam_rfi_width));
set_param(name, 'din_point', num2str(beam_rfi_point));
set_param(name, 'pow_add_dly', num2str(rfi_pow_pow_add_dly));
set_param(name, 'pow_mult_dly', num2str(rfi_pow_pow_mult_dly));
set_param(name, 'post_pow_dly', num2str(rfi_pow_post_pow_dly));
set_param(name, 'acc_width', num2str(rfi_pow_acc_width));
set_param(name, 'post_acc_dly', num2str(rfi_pow_post_acc_dly));
set_param(name, 'post_acc_shift', num2str(rfi_pow_post_acc_shift));
set_param(name, 'post_acc_width', num2str(rfi_pow_post_acc_conv_width));
set_param(name, 'post_acc_point', num2str(rfi_pow_post_acc_conv_point));
set_param(name, 'shift_out', num2str(rfi_pow_dout_shift));
set_param(name, 'dout_width', num2str(rfi_pow_dout_width));
set_param(name, 'dout_point', num2str(rfi_pow_dout_point));
set_param(name, 'cmult_add_dly', num2str(rfi_pow_cmult_add_dly));
set_param(name, 'cmult_mult_dly', num2str(rfi_pow_cmult_mult_dly));

%rfi phase calculation

disp('Configuring RFI division (actually is atan)');
name = strcat(model_name, '/pre_phase_delay');
set_param(name, 'lat', num2str(rfi_phase_din_delay));


name = strcat(model_name, '/phase_calc');
set_param(name, 'din_width', num2str(rfi_phase_din_width));
set_param(name, 'din_point', num2str(rfi_phase_din_point));
%set_param(name, 'scale_max_shift', num2str(rfi_autoscale_max_shift));
%set_param(name, 'scale_min_shift', num2str(rfi_autoscale_min_shift));
%set_param(name, 'pre_cordic_shift', num2str(rfi_pre_cordic_shift));
set_param(name, 'pre_cordic_width', num2str(rfi_pre_cordic_width));
set_param(name, 'pre_cordic_point', num2str(rfi_pre_cordic_point));
set_param(name, 'cordic_iters', num2str(rfi_cordic_iters));


