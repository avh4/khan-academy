import os, traceback


def get_mangled_playlist_name(playlist_name):
    for char in " :()":
        playlist_name = playlist_name.replace(char, "")
    return playlist_name
    
    
def write_meta_files(playlist, description):
    try:
        playlist_id = get_mangled_playlist_name(playlist)
        os.chdir(cwd + "/Khan Academy/videos/" + playlist_id)    
        data = """<metadata>
  <identifier>KhanAcademy_%s</identifier>
  <title>%s</title>
  <collection>opensource_movies</collection>
  <mediatype>movies</mediatype>
  <description>%s</description> 
  <creator>Salman Khan</creator>
  <production_company>Khan Academy</production_company>  
  <licenseurl>http://creativecommons.org/licenses/by-sa/3.0/us/</licenseurl>
</metadata>""" % (playlist_id, playlist, description)
        file = open("KhanAcademy_" + playlist_id + "_meta.xml", "w")
        file.write(data)
        file.close()
    
        file = open("KhanAcademy_" + playlist_id + "_files.xml", "w")
        file.write("<files/>")
        file.close()
    except:
        traceback.print_exc()


if __name__ == "__main__":
    # use the download_scripts to get one or more playlists
    # you can change the -f option of youtube-dl.py to get different formats, video resolutions, etc.
    # documented here: http://en.wikipedia.org/wiki/YouTube
    
    # write the meta data files needed for uploading to archive.org
    # http://www.archive.org/help/contrib-advanced.php
    cwd = os.getcwd()
    write_meta_files('Algebra', 'This is the original Algebra playlist on the Khan Academy and is where Sal continues to add videos that are not done for some other organization. It starts from very basic algebra and works its way through algebra II. This is the best algebra playlist to start at if you\'ve never seen algebra before. Once you get your feet wet, you may want to try some of the videos in the "Algebra I Worked Examples" playlist.')
    write_meta_files('Algebra I Worked Examples', '180 Worked Algebra I examples (problems written by the Monterey Institute of Technology and Education). You should look at the "Algebra" playlist if you\'ve never seen algebra before or if you want instruction on topics in Algebra II. Use this playlist to see a ton of example problems in every topic in the California Algebra I Standards. If you can do all of these problems on your own, you should probably test out of Algebra I (seriously).')
    write_meta_files("Arithmetic", "The most basic of the math playlists. Start here if you have very little background in math fundamentals (or just want to make sure you do). After watching this playlist, you should be ready for the pre-algebra playlist.")
    write_meta_files("Banking and Money", "Videos on how banks work and how money is created.")
    write_meta_files('Biology', 'Covers topics seen in a first year college or high school biology course.')    
    write_meta_files("Brain Teasers", "Random logic puzzles and brain teasers. Fun to do and useful for many job interviews!")      
    write_meta_files('CAHSEE Example Problems', "Sal working through the 53 problems from the practice test available at http://www.cde.ca.gov/ta/tg/hs/documents/mathpractest.pdf for the CAHSEE (California High School Exit Examination). Clearly useful if you're looking to take that exam. Probably still useful if you want to make sure you have a solid understanding of basic high school math.")
    write_meta_files('Calculus', 'Topics covered in the first two or three semester of college calculus. Everything from limits to derivatives to integrals to vector calculus. Should understand the topics in the pre-calculus playlist first (the limit videos are in both playlists)')    
    write_meta_files('California Standards Test: Algebra I', 'Sal works through the problems from the CA Standards released questions: http://www.cde.ca.gov/ta/tg/sr/documents/rtqalg1.pdf . Good videos to review Algebra I (The "Algebra I Worked Examples" playlist is more comprehensive and should probably be watched first).')
    write_meta_files('California Standards Test: Algebra II', 'Sal works through 80 questions taken from the California Standards Test for Algebra II. Good place to review the major topics in Algebra II even if you\'re not in California. Many of these topics are taugt in more depth in the "Algebra" playlist.')
    write_meta_files("California Standards Test: Geometry", "Sal does the 80 problems from the released questions from the California Standards Test for Geometry. Test at http://www.cde.ca.gov/ta/tg/sr/documents/rtqgeom.pdf . Basic understanding of Algebra I necessary.")
    write_meta_files("Chemistry", "Videos on chemistry (roughly covering a first-year high school or college course).")
    write_meta_files('ck12.org Algebra 1 Examples', "Select problems from ck12.org's Algebra 1 FlexBook (Open Source Textbook). This is a good playlist to review if you want to make sure you have a good understanding of all of the major topics in Algebra I.")
    write_meta_files("Credit Crisis", "Videos on the causes and effects of the credit crisis/crunch.")
    write_meta_files("Current Economics", "Discussions of economic topics and how they relate to current events.")
    write_meta_files("Developmental Math", "Worked developmental math examples from the Monterey Institute.  These start pretty basic and would prepare a student for the Algebra I worked examples")
    write_meta_files('Differential Equations', 'Topics covered in a first year course in differential equations. Need to understand basic differentiation and integration from Calculus playlist before starting here.')    
    write_meta_files("Finance", "Videos on finance and macroeconomics")
    write_meta_files("Geithner Plan", "Videos on the Geithner Plan to solve the banking crisis.")
    write_meta_files("Geometry", "Videos on geometry. Basic understanding of Algebra I necessary. After this, you'll be ready for Trigonometry.")
    write_meta_files('GMAT Data Sufficiency', 'Sal works through 155 data sufficiency problems in the GMAC GMAT Review book (so using real GMAT problems). Buy the book, then watch the videos.')
    write_meta_files('GMAT: Problem Solving', 'Sal works through tbe 249 problem solving (math) questions in the official GMAC GMAT book.')
    write_meta_files('History', 'The history of the world (eventually)!')    
    write_meta_files('Khan Academy-Related Talks and Interviews', 'Collection of interviews with and presentations by Salman Khan. Also a few other mentions of Khan Academy at other talks.')
    write_meta_files('Linear Algebra', "Matrices, vectors, vector spaces, transformations. Covers all topics in a first year college linear algebra course. This is an advanced course normally taken by science or engineering majors after taking at least two semesters of calculus (although calculus really isn't a prereq) so don't confuse this with regular high school algebra.")    
    write_meta_files('MA Tests for Education Licensure (MTEL) -Pre-Alg', 'Massachusetts Tests for Education Licensure (MTEL) General Curriculum (03) Practice Test explained by Sal. Good problems for deep understanding of pre-algebra concepts.')    
    write_meta_files('Organic Chemistry', 'Topics covered in college organic chemistry course. Basic understanding of basic high school or college chemistry assumed')  
    write_meta_files('Paulson Bailout', 'Videos to help understand the bailout.')    
    write_meta_files('Physics', 'Projectile motion, mechanics and electricity and magnetism. Solid understanding of algebra and a basic understanding of trigonometry necessary.')    
    write_meta_files("Pre-algebra", 'Videos on pre-algebra. Should be ready for the "Algebra" playlist if you understand everything here.')
    write_meta_files('Precalculus', 'Non-trigonometry pre-calculus topics. Solid understanding of all of the topics in the "Algebra" playlist should make this playlist pretty digestible.')    
    write_meta_files('Probability', 'Basic probability. Should have a reasonable grounding in basic algebra before watching')    
    write_meta_files('SAT Preparation', 'I am going to work through every problem in the College Board "Official SAT Study Guide." You should take the practice tests on your own, grade them and then use these videos to understand the problems you didn\'t get or review. Have fun!')
    write_meta_files('Statistics', 'Introduction to statistics. Will eventually cover all of the major topics in a first-year statistics course (not there yet!)')    
    write_meta_files('Trigonometry', 'Videos on trigonometry. Watch the "Geometry" playlist first if you have trouble understanding the topics covered here.')    
    write_meta_files("Valuation and Investing", "Building blocks and case studies on the financial analysis and valuation of public equities.")
    write_meta_files("Venture Capital and Capital Markets", "All of the sources of funding (capital) for a business.")

    # connect to the archive.org ftp server (items-uploads.archive.org), I used FileZilla 
    # for each directory:
    #    upload, then redo any failed transfers 
    #    rename directory on archive.org with prefix KhanAcademy_
    #    change the dir argument in the below url, and load it in a browser
    #    check for any error messages returned

    #http://www.archive.org/services/contrib-submit.php?user_email=<your email>&server=items-uploads.archive.org&dir=KhanAcademy_BrainTeasers