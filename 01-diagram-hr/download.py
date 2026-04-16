import requests

def download_parsec_isochrone(log_age=9.0, z=0.019, output_file='isochrone_parsec.dat'):
    """
    Baixa isocrona do CMD 3.7 (Padova/PARSEC) via HTTP.
    log_age: logaritmo da idade (9.0 = 1 Gyr, 8.0 = 100 Myr)
    z: metalicidade (0.019 = solar)
    """
    url = "http://stev.oapd.inaf.it/cgi-bin/cmd_3.7"
    
    params = {
        'submit_form': 'Submit',
        'cmd_version': '3.7',
        # sistema fotométrico — Gaia EDR3
        'photsys_file': 'YBC_tab_mag_odfnew/tab_mag_gaiaEDR3.dat',
        'photsys_version': 'YBCnewVega',
        'dust_sourceM': 'nodustM',
        'dust_sourceC': 'nodustC',
        'extinction_av': '0.0',
        'imf_file': 'tab_imf/imf_kroupa_orig.dat',
        'isoc_isagelog': '1',
        'isoc_agelow': str(log_age),
        'isoc_ageupp': str(log_age),
        'isoc_dage': '0',
        'isoc_zlow': str(z),
        'isoc_zupp': str(z),
        'isoc_dz': '0',
        'output_kind': '0',             
        'output_evstage': '1',          
        'lf_maginf': '-15',
        'lf_magsup': '20',
    }
    
    print("Baixando isocrona do PARSEC...")
    response = requests.post(url, data=params)
    
    if response.status_code != 200:
        print(f"Erro HTTP: {response.status_code}")
        return None
    
    import re
    match = re.search(r'href="(.*?output.*?\.dat)"', response.text)
    if not match:
        print("Não encontrou link do arquivo. Resposta:")
        print(response.text[:500])
        return None
    
    dat_url = "http://stev.oapd.inaf.it" + match.group(1)
    print(f"Link encontrado: {dat_url}")
    
    dat_response = requests.get(dat_url)
    with open(output_file, 'w') as f:
        f.write(dat_response.text)
    
    print(f"Salvo em: {output_file}")
    return output_file

download_parsec_isochrone(log_age=9.0, z=0.019)