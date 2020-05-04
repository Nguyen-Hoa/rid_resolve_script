import os
from requests import get
from html.parser import HTMLParser
import shutil

pdf_dir = './pdfs'          # Where PDFs are stored
out_dir = './named_files'   # Where named PDFS are stored

if os.path.isdir(out_dir) == False:
    os.mkdir(out_dir)

class TitleTagParser (HTMLParser):
    """ 
        HTMLParser object to grab 
        linenumber from <title></title> tags
    """
    
    start_title_pos = list()
    
    def handle_starttag(self, tag, attrs):
        if tag == 'title':
            self.start_title_pos.append(self.getpos())

    def clean(self):
        self.start_title_pos.clear()

def html2title(url, ref_id):
    """ 
        Scrape for title tags given a url and reference ID.
            url     = the source to search for ref_id.
            ref_id  = the id we want to resolve a title to. 
        return -1 if not found
        return <title> element with title
    """
    
    response = get(url + ref_id)
    raw = response.text
    
    parser = TitleTagParser()
    parser.feed(raw)
    raw = raw.splitlines()
    title = raw[parser.start_title_pos[0][0]-1]
    parser.clean()
    parser.reset()

    if 'not recognized' in title:
        # not found in arXiv
        return -1
    elif 'Error' in title:
        # not found in ACM DL
        return -1
    else:
        return title

# For all files in PDF directory
for filename in os.listdir(pdf_dir):
    
    # Only support .pdf
    if '.pdf' not in filename:
        continue

    # remove suffix '.pdf' to obtain reference number
    ref_id = filename[:-4]
    
    # Try arXiv
    arxiv_url = 'https://arxiv.org/abs/'
    title = html2title(arxiv_url, ref_id)
    
    # Try ACM DL
    if title == -1:
        acmdl_url = 'https://dl.acm.org/doi/10.1145/'
        title = html2title(acmdl_url, ref_id)

    # Remove tags and replace whitespaces with underscores  
    clean_title = title.replace('<title>', '').replace('</title>','')
    clean_title = clean_title.replace(' ', '_')
    
    # Create a copy of .pdf with resolved title in output directory
    print('Found \'' + clean_title + '\' for ' + ref_id)
    shutil.copyfile(pdf_dir+'/'+filename, out_dir+'/'+clean_title+'.pdf')

print('done')

