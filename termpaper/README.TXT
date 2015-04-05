README.TXT
Revised circa August 2013

This folder contains the files needed to create your term paper using the ACM conference style.

You will find LaTeX packages available on the web for free download on your own PCs or Macs. Please use one of these as they will make this process smoother. You can also use the CS department's LaTeX installation, which is described below.

You will need to edit the file, termpaper.tex, and the file, term paper.bib. The first file contains the text of your paper, and the second file contains the bibliography of cited papers in BiBTeX style. Once both files are edited to your satisfaction, you will need to compile them using LaTeX and BibTeX to generate the required PDF file needed for submission.
	latex termpaper
	bibtex termpaper
	latex termpaper
	latex termpaper

To generate the PDF file for submission, you may use a dvi2pdf program or replace the above sequence by the following:
	pdflatex termpaper
	bibtex termpaper
	pdflatex termpaper
	pdflatex termpaper

The sequences shown above are critical to generating the correct paper with appropriate citations and cross-references.

Submit the generated termpaper.pdf to the dropbox.

Notes: 
   1. For your convenience, the initial generated pdf has been copied to a separate file TERMPAPER_INITIAL.PDF so that you can refer to it for formatting help and suggestions. Don't submit this file by mistake. 
   2. The file GUIDE.PDF provides more help with the ACm conference style.