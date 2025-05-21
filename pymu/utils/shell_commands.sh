find /N/project/fads_ng/analyst_reports_project/data/analyst_reports_pdf -maxdepth 1 -name '*.pdf' -print0 | xargs -0 -n 1 basename | sed 's/\.pdf$//' | sort > pdfs.txt
find /N/project/fads_ng/analyst_reports_project/data/analyst_reports_txt_page1 -maxdepth 1 -name '*_pages1.txt' -print0 | xargs -0 -n 1 basename | sed 's/_pages1\.txt$//' | sort > txts.txt
comm -23 pdfs.txt txts.txt | wc -l
comm -23 pdfs.txt txts.txt > missing_files.txt

