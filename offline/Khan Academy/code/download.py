import sys, urllib, os
from video_mapping import video_mapping
        
        
playlist_mapping = {
    "Algebra": "Algebra",
    "Arithmetic": "Arithmetic",
    'BankingandMoney': "BankingAndMoney",
    "Biology": "Biology",
    "BrainTeasers": "BrainTeasers",
    'CAHSEEExampleProblems': "CahseeExampleProblems",
    "Calculus": "Calculus",
    'CaliforniaStandardsTest-AlgebraI': "CaliforniaStandardsTestAlgebraI",
    'CaliforniaStandardsTest-AlgebraII': "CaliforniaStandardsTestAlgebraIi",
    "CaliforniaStandardsTest-Geometry": "CaliforniaStandardsTestGeometry",
    "Chemistry": "Chemistry",
    "CreditCrisis": "CreditCrisis",
    "CurrentEconomics": "CurrentEconomics",
    "DifferentialEquations": "DifferentialEquations",
    "Finance": "Finance",
    "GeithnerPlan": "GeithnerPlan",
    "Geometry": "Geometry",
    "GMATDataSufficiency": "GmatDataSufficiency",
    'GMAT-ProblemSolving': "GmatProblemSolving",
    "LinearAlgebra": "LinearAlgebra",
    'MATestsforEducationLicensure(MTEL)-Pre-Alg': "MaTestsForEducationLicensuremtel-pre-alg",
    "PaulsonBailout": "PaulsonBailout",
    "Physics": "Physics",
    "Pre-algebra": "Pre-algebra",
    "Precalculus": "Precalculus",
    "Probability": "Probability",
    "SATPreparation": "SatPreparation",
    "SingaporeMath": "SingaporeMath",
    "Statistics": "Statistics",
    "Trigonometry": "Trigonometry",
    "ValuationandInvesting": "ValuationAndInvesting",
    'VentureCapitalandCapitalMarkets': "VentureCapitalAndCapitalMarkets",
    "History": "history",
}


def urlretrieve(urlfile, fpath):
    chunk = 2**20
    f = open(fpath, "wb")
    while 1:
        data = urlfile.read(chunk)
        if not data:
            break
        f.write(data)
        print "*",
    print
    

cwd = os.getcwd()    
playlist = sys.argv[1]
videos = video_mapping[playlist]
folder = "../videos/" + playlist
archive_org_url = "http://www.archive.org/download/KhanAcademy/"
ao_playlist_name = playlist_mapping.get(playlist)

if ao_playlist_name:
    download_filename = ao_playlist_name + ".7z"
    if not os.path.exists(download_filename):
        urlfile = urllib.urlopen(archive_org_url + download_filename)
        print "downloading", archive_org_url + download_filename
        urlretrieve(urlfile, download_filename)

    if not os.path.exists(folder): 
        os.chdir("../code")
        os.system('7za.exe e ../download_scripts/'+download_filename+' -o' + folder)
        os.chdir(folder)        
        filename_mapping = {}
        for title, youtube_id, readable_id in videos:
            filename_mapping[title + ".flv"] = readable_id + ".flv"
        for filename in os.listdir("."):
            items = filename.split(".")
            if len(items) > 1:
                ext = items[-1]        
                if ext == "flv":  
                    if filename in filename_mapping:
                        os.rename(filename, filename_mapping[filename])
                    else:
                        print "video not found in datastore, deleting:", filename 
                        os.remove(filename)

os.chdir(cwd + "/../code")
if not os.path.exists(folder):
    os.mkdir(folder)
for title, youtube_id, readable_id in videos:
    if os.path.exists(folder + '/' + readable_id + ".flv"):
        print "already downloaded", readable_id
    else:
        os.system('/Python25/python.exe youtube-dl.py -f 34 -icw -o "' + folder + '/' + readable_id + '.flv" http://www.youtube.com/watch?v=' + youtube_id)

                         