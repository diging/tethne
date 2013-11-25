import sys
sys.path.append("/Users/erickpeirson/Dropbox/DigitalHPS/Scripts/tethne")
import tethne.readers as rd
import tethne.networks as nt
import tethne.analyze as az

    
if __name__ == "__main__":
    path = "/Users/erickpeirson/Dropbox/DigitalHPS/MPIWG Department Baldwin/WoS data/Plant Journal 1991(v1) - 2013-11"

    wos_list = rd.wos.parse_from_dir(path)
    papers = rd.wos.wos2meta(wos_list)
    
    start = 1998
    end = 2010
    chunk = 4
    
    name = 'BALDWIN I'
    
    cc = az.workflow.closeness_introgression(papers, name, start, end, chunk)
    
    print len(papers)
    print cc