library IEEE;
use IEEE.std_logic_1164.all;

entity pfb_fft_8in_2048ch is
  port (
    ce_1: in std_logic; 
    clk_1: in std_logic; 
    dat0: in std_logic_vector(7 downto 0); 
    dat1: in std_logic_vector(7 downto 0); 
    dat2: in std_logic_vector(7 downto 0); 
    dat3: in std_logic_vector(7 downto 0); 
    dat4: in std_logic_vector(7 downto 0); 
    dat5: in std_logic_vector(7 downto 0); 
    dat6: in std_logic_vector(7 downto 0); 
    dat7: in std_logic_vector(7 downto 0); 
    sync_in: in std_logic; 
    ch0: out std_logic_vector(35 downto 0); 
    ch1: out std_logic_vector(35 downto 0); 
    ch2: out std_logic_vector(35 downto 0); 
    ch3: out std_logic_vector(35 downto 0); 
    fft_ovf: out std_logic_vector(1 downto 0); 
    sync_out: out std_logic
  );
end pfb_fft_8in_2048ch;

architecture structural of pfb_fft_8in_2048ch is
begin
end structural;

