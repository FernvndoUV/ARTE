import yaml, subprocess

if __name__ == '__main__':
    f = open('configuration.yml', 'r')
    config = yaml.load(f, Loader=yaml.loader.SafeLoader)
    f.close()
    cmd = ['calibrate_adc5g',
            '-i', config['roach_ip'],
            '-gf', '10',
            '-gp', '8',
            '--zdok0snap', 'adcsnap0 adcsnap1',
            '--zdok1snap', 'adcsnap2 adcsnap3',
            '--ns', '128',
            '-bw', config['bandwidth']]
    if(config['calibrate']['do_mcmm']):
        cmd.append('-dm')
    if(config['calibrate']['do_ogp']):
        cmd.append('-do')
    if(config['calibrate']['do_inl']):
        cmd.append('-di')
    if(config['calibrate']['plot_snap']):
        cmd.append('-psn')
    if(config['calibrate']['plot_spect']):
        cmd.append('-psp')

    subprocess.call(cmd)


