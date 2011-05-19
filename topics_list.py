import logging

# Each leaf node in PLAYLIST_STRUCTURE is a tuple of form:
#   ("<Playlist short description for jump bar>", "<Playlist title>", "<Jump bar URL override (optional)>")

PLAYLIST_STRUCTURE = [
    {
        "Math": [
            ("Arithmetic", "Arithmetic"),
            {
                "Developmental Math": [
                    ("Developmental Math 1", "Developmental Math"),
                    ("Developmental Math 2", "Developmental Math 2"),
                ]
            },
            {
                "Pre-Algebra": [
                    ("Core Pre-Algebra", "Pre-algebra"),
                    ("Worked Examples 1", "MA Tests for Education Licensure (MTEL) -Pre-Alg"),
                ]
            },
            ("Brain Teasers", "Brain Teasers"),
            {
                "Algebra": [
                    ("Core Algebra", "Algebra"),
                    ("Worked Examples 1", "California Standards Test: Algebra I"),
                    ("Worked Examples 2", "ck12.org Algebra 1 Examples"),
                    ("Worked Examples 3", "California Standards Test: Algebra II"),
                    ("Worked Examples 4", "Algebra I Worked Examples"),
                ]
            },
            {
                "Geometry": [
                    ("Core Geometry", "Geometry"),
                    ("Worked Examples 1", "California Standards Test: Geometry"),
                ]
            },
            ("Trigonometry", "Trigonometry"),
            ("Probability", "Probability"),
            ("Statistics", "Statistics"),
            ("Precalculus", "Precalculus"),
            ("Calculus", "Calculus"),
            ("Differential Equations", "Differential Equations"),
            ("Linear Algebra", "Linear Algebra"),
        ]
    },
    {
        "Science": [
            ("Biology", "Biology"),
            ("Chemistry", "Chemistry"),
            ("Physics", "Physics"),
            ("Organic Chemistry", "Organic Chemistry"),
            ("Cosmology and Astronomy", "Cosmology and Astronomy"),
        ],
    },
    {
        "Humanities & Other": [
            ("History", "History"),
            {
                "Finance": [
                    ("Core Finance", "Finance"),
                    ("Banking and Money", "Banking and Money"),
                    ("Valuation and Investing", "Valuation and Investing"),
                    ("Venture Capital and Capital Markets", "Venture Capital and Capital Markets"),
                    ("Credit Crisis", "Credit Crisis"),
                    ("Paulson Bailout", "Paulson Bailout"),
                    ("Geithner Plan", "Geithner Plan"),
                    ("Current Economics", "Current Economics"),
                    ("Currency", "Currency"),
                ]
            },
        ],
    },
    {
        "Test Prep": [
            ("SAT Math", "SAT Preparation", "/sat"),
            {
                "GMAT": [
                    ("Problem Solving", "GMAT: Problem Solving", "/gmat#problem_solving"),
                    ("Data Sufficiency", "GMAT Data Sufficiency", "/gmat"),
                ]
            },
            ("CAHSEE", "CAHSEE Example Problems"),
            ("IIT JEE", "IIT JEE Questions"),
            ("Singapore Math", "Singapore Math"),
        ],
    },
    ("Talks and Interviews", "Khan Academy-Related Talks and Interviews")
]

# Each DVD needs to stay under 4.4GB

DVDs_dict = {
    'Math': [ # 3.85GB
        'Arithmetic',
        'Pre-algebra',
        'Algebra',
        'Geometry',
        'Trigonometry',
        'Probability',
        'Statistics',
        'Precalculus',
    ],
    'Advanced Math': [ # 4.11GB
        'Calculus',
        'Differential Equations',
        'Linear Algebra',
    ],        
    'Math Worked Examples': [ # 3.92GB
        'Developmental Math',
        'Developmental Math 2',
        'Algebra I Worked Examples',
        'ck12.org Algebra 1 Examples',
        'Singapore Math',
    ],
    'Chemistry': [ # 2.92GB
        'Chemistry',
        'Organic Chemistry',
    ],
    'Science': [ # 3.24GB
        'Cosmology and Astronomy',
        'Biology',
        'Physics',
    ],
    'Finance': [ # 2.84GB
        'Finance',
        'Banking and Money',
        'Valuation and Investing',
        'Venture Capital and Capital Markets',
        'Credit Crisis',
        'Paulson Bailout',
        'Geithner Plan',
        'Current Economics',
        'Currency',
    ],
    'Test Prep': [ # 3.37GB
        'MA Tests for Education Licensure (MTEL) -Pre-Alg',
        'California Standards Test: Algebra I',
        'California Standards Test: Algebra II',
        'California Standards Test: Geometry',        
        'CAHSEE Example Problems',
        'SAT Preparation',
        'IIT JEE Questions',
        'GMAT: Problem Solving',
        'GMAT Data Sufficiency',        
    ],
    'Misc': [ # 1.93GB
        'Talks and Interviews',
        'History',   
        'Brain Teasers',
    ],    
}

# replace None with the DVD name above that you want to burn
# this will restrict the homepage to only show the playlists from that list
DVD_list = DVDs_dict.get(None) #'Math'

def sorted_playlist_titles():
    playlist_titles = []
    append_playlist_titles(playlist_titles, PLAYLIST_STRUCTURE)
    playlist_titles.sort()
    return playlist_titles

def append_playlist_titles(playlist_titles, obj):
    type_obj = type(obj)
    if type_obj == dict:
        for key in obj:
            append_playlist_titles(playlist_titles, obj[key])
    elif type_obj == list:
        for val in obj:
            append_playlist_titles(playlist_titles, val)
    elif type_obj == tuple:
        playlist_titles.append(obj[1])

if DVD_list:
    topics_list = all_topics_list = DVD_list
else:
    topics_list = all_topics_list = sorted_playlist_titles()

