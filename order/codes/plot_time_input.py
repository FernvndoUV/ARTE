import yaml, subprocess

if __name__ == '__main__':
    f = open('configuration.yml', 'r')
    config = yaml.load(f, Loader=yaml.loader.SafeLoader)
    f.close()
    cmd = ['plot_snapshots.py', '--ip', config['roach_ip'],
           '--snapnames', 'adcsnap0', 'adcsnap1', 'adcsnap2', 'adcsnap3',
           '--dtype', '>i1',
           '--nsamples', '200']
    subprocess.call(cmd)
