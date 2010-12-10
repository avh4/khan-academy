import copy


# Each DVD needs to stay under 4.4GB

math_DVD_list = [ # 3.6GB
    'Arithmetic',
    'Pre-algebra',
    'Algebra',
    'Geometry',
    'Trigonometry',
    'Probability',
    'Statistics',
    'Precalculus'
]

advanced_math_DVD_list = [ # 4.0GB
    'Calculus',
    'Differential Equations',
    'Linear Algebra'
]        

math_worked_examples_DVD_list = [ # 4.2GB
    'Developmental Math',
    'MA Tests for Education Licensure (MTEL) -Pre-Alg',
    'Algebra I Worked Examples',
    'ck12.org Algebra 1 Examples',
    'California Standards Test: Algebra I',
    'California Standards Test: Algebra II',
    'California Standards Test: Geometry',
    'Singapore Math'
]

chemistry_DVD_list = [ # 2.9GB
    'Chemistry',
    'Organic Chemistry',
]

science_DVD_list = [ # 2.8GB
    'Cosmology and Astronomy',
    'Biology',
    'Physics'
]

finance_DVD_list = [ # 2.5GB
    'Finance',
    'Banking and Money',
    'Valuation and Investing',
    'Venture Capital and Capital Markets',
    'Credit Crisis',
    'Paulson Bailout',
    'Geithner Plan',
    'Current Economics',
    'Currency'
]

test_prep_DVD_list = [ # 2.0GB
    'SAT Preparation',
    'GMAT: Problem Solving',
    'GMAT Data Sufficiency',
    'CAHSEE Example Problems'
]

# replace False with the DVD_list above that you want to burn
# this will restrict the homepage to only show the playlists from that list
DVD_list = False # math_DVD_list

if DVD_list:
    topics_list = all_topics_list = DVD_list
else:
    topics_list = []
    topics_list.append('Arithmetic')
    topics_list.append('Chemistry')
    topics_list.append('Developmental Math')
    topics_list.append('Pre-algebra')
    topics_list.append('MA Tests for Education Licensure (MTEL) -Pre-Alg')
    topics_list.append('Geometry')
    topics_list.append('California Standards Test: Geometry')
    topics_list.append('Current Economics')
    topics_list.append('Banking and Money')
    topics_list.append('Venture Capital and Capital Markets')
    topics_list.append('Finance')
    topics_list.append('Credit Crisis')
    topics_list.append('Currency')
    topics_list.append('Valuation and Investing')
    topics_list.append('Geithner Plan')
    topics_list.append('Algebra')
    topics_list.append('Algebra I Worked Examples')
    topics_list.append('ck12.org Algebra 1 Examples')
    topics_list.append('California Standards Test: Algebra I')
    topics_list.append('California Standards Test: Algebra II')
    topics_list.append('Brain Teasers')
    topics_list.append('Biology')
    topics_list.append('Trigonometry')
    topics_list.append('Precalculus')
    topics_list.append('Statistics')
    topics_list.append('Probability')
    topics_list.append('Calculus')
    topics_list.append('Differential Equations')
    topics_list.append('Khan Academy-Related Talks and Interviews')
    topics_list.append('History')
    topics_list.append('Organic Chemistry')
    topics_list.append('Linear Algebra')
    topics_list.append('Physics')
    topics_list.append('Paulson Bailout')
    topics_list.append('CAHSEE Example Problems')
    topics_list.append('Cosmology and Astronomy')
    topics_list.sort()

    all_topics_list = copy.copy(topics_list)
    all_topics_list.append('SAT Preparation')        
    all_topics_list.append('GMAT: Problem Solving')
    all_topics_list.append('GMAT Data Sufficiency')        
    all_topics_list.append('Singapore Math')        
    all_topics_list.sort()  